"""Testes do relatório de turma, exportação (CSV/PDF) e do "meu-resultado" do aluno."""


def _finaliza_simulado(client, h_gestor, h_aluno, turma_id, *, acertar=True, quantidade=3):
    r = client.post(
        "/simulados",
        headers=h_gestor,
        json={
            "turma_id": turma_id,
            "titulo": "Relatório",
            "serie": "9º ano",
            "materia": "Matemática",
            "quantidade": quantidade,
            "seed": 7,
        },
    )
    assert r.status_code == 201, r.text
    sid = r.json()["id"]
    client.post(f"/simulados/{sid}/gerar", headers=h_gestor, json={})
    client.post(f"/simulados/{sid}/liberar", headers=h_gestor, json={})
    prev = client.get(f"/simulados/{sid}/preview", headers=h_gestor).json()["questoes"]
    for q in prev:
        if acertar:
            alt = next(a for a in q["alternativas"] if a["correta"])
        else:
            alt = next(a for a in q["alternativas"] if not a["correta"])
        client.post(
            "/respostas",
            headers=h_aluno,
            json={
                "simulado_id": sid,
                "questao_id": q["questao_id"],
                "alternativa_id": alt["alternativa_id"],
            },
        )
    client.post(f"/simulados/{sid}/finalizar", headers=h_gestor, json={})
    return sid


def test_relatorio_turma_basico(client, h_gestor, h_aluno, dados):
    _finaliza_simulado(client, h_gestor, h_aluno, dados["turma_id"], acertar=True)
    r = client.get(f"/relatorios/turma/{dados['turma_id']}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["alunos"] == 2  # conftest cria 2 alunos na turma
    assert corpo["media_turma"] == 10.0  # só o aluno 1 respondeu, e acertou tudo
    assert corpo["simulados_corrigidos"] == 1
    assert isinstance(corpo["conteudos"], list)


def test_relatorio_turma_inexistente_404(client, h_gestor):
    assert client.get("/relatorios/turma/9999", headers=h_gestor).status_code == 404


def test_relatorio_exige_gestor(client, h_aluno, dados):
    r = client.get(f"/relatorios/turma/{dados['turma_id']}", headers=h_aluno)
    assert r.status_code == 403


def test_export_csv(client, h_gestor, h_aluno, dados):
    _finaliza_simulado(client, h_gestor, h_aluno, dados["turma_id"], acertar=False)
    r = client.get(
        f"/relatorios/turma/{dados['turma_id']}/export?formato=csv", headers=h_gestor
    )
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "Turma" in r.text and "Alunos" in r.text


def test_export_pdf(client, h_gestor, h_aluno, dados):
    _finaliza_simulado(client, h_gestor, h_aluno, dados["turma_id"], acertar=False)
    r = client.get(
        f"/relatorios/turma/{dados['turma_id']}/export?formato=pdf", headers=h_gestor
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


def test_meu_resultado(client, h_gestor, h_aluno, dados):
    sid = _finaliza_simulado(client, h_gestor, h_aluno, dados["turma_id"], acertar=True)
    r = client.get(f"/simulados/{sid}/meu-resultado", headers=h_aluno)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["nota"] == 10.0
    assert len(corpo["questoes"]) == 3
    assert all(q["acertou"] for q in corpo["questoes"])
    assert all(q["sua_resposta"] == q["gabarito"] for q in corpo["questoes"])


def test_meu_resultado_so_apos_finalizar(client, h_gestor, h_aluno, dados):
    # Simulado liberado mas ainda não finalizado -> 409.
    r = client.post(
        "/simulados",
        headers=h_gestor,
        json={
            "turma_id": dados["turma_id"],
            "titulo": "x",
            "serie": "9º ano",
            "materia": "Matemática",
            "quantidade": 3,
        },
    )
    sid = r.json()["id"]
    client.post(f"/simulados/{sid}/gerar", headers=h_gestor, json={})
    client.post(f"/simulados/{sid}/liberar", headers=h_gestor, json={})
    rr = client.get(f"/simulados/{sid}/meu-resultado", headers=h_aluno)
    assert rr.status_code == 409


def test_meu_resultado_gestor_nao_tem(client, h_gestor, h_aluno, dados):
    sid = _finaliza_simulado(client, h_gestor, h_aluno, dados["turma_id"], acertar=True)
    r = client.get(f"/simulados/{sid}/meu-resultado", headers=h_gestor)
    assert r.status_code == 403
