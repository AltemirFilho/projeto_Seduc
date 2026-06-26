"""Listagem de simulados (gestão + aluno), resumo e monitoramento ao vivo."""


def _cria(client, h_gestor, turma_id, titulo="Simulado X", quantidade=3):
    r = client.post(
        "/simulados",
        headers=h_gestor,
        json={
            "turma_id": turma_id,
            "titulo": titulo,
            "serie": "9º ano",
            "materia": "Matemática",
            "quantidade": quantidade,
            "seed": 7,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _gerar(client, h_gestor, sid):
    assert (
        client.post(f"/simulados/{sid}/gerar", headers=h_gestor, json={}).status_code
        == 200
    )


def _liberar(client, h_gestor, sid):
    assert (
        client.post(f"/simulados/{sid}/liberar", headers=h_gestor, json={}).status_code
        == 200
    )


def test_listar_simulados_do_gestor(client, h_gestor, dados):
    _cria(client, h_gestor, dados["turma_id"], titulo="A")
    _cria(client, h_gestor, dados["turma_id"], titulo="B")
    r = client.get("/simulados", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["meta"]["total"] == 2
    assert {s["titulo"] for s in corpo["dados"]} == {"A", "B"}
    s = corpo["dados"][0]
    for chave in ("id", "titulo", "status", "turma_id", "turma", "total_questoes", "criado_em"):
        assert chave in s


def test_listar_filtra_por_status(client, h_gestor, dados):
    sid = _cria(client, h_gestor, dados["turma_id"])
    _gerar(client, h_gestor, sid)
    _liberar(client, h_gestor, sid)
    _cria(client, h_gestor, dados["turma_id"])  # permanece rascunho
    r = client.get("/simulados?status=liberado", headers=h_gestor)
    assert r.status_code == 200
    assert [s["id"] for s in r.json()["dados"]] == [sid]


def test_status_invalido_da_422(client, h_gestor):
    r = client.get("/simulados?status=banana", headers=h_gestor)
    assert r.status_code == 422
    assert r.json()["codigo"] == "dados_invalidos"


def test_obter_resumo_simulado(client, h_gestor, dados):
    sid = _cria(client, h_gestor, dados["turma_id"], titulo="Resumo")
    r = client.get(f"/simulados/{sid}", headers=h_gestor)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == sid
    assert r.json()["titulo"] == "Resumo"


def test_aluno_nao_lista_simulados_da_gestao(client, h_aluno):
    assert client.get("/simulados", headers=h_aluno).status_code == 403


def test_disponiveis_so_traz_liberado_da_turma(client, h_gestor, h_aluno, dados):
    _cria(client, h_gestor, dados["turma_id"], titulo="Rascunho")  # não aparece
    sid = _cria(client, h_gestor, dados["turma_id"], titulo="Liberado")
    _gerar(client, h_gestor, sid)
    _liberar(client, h_gestor, sid)
    r = client.get("/simulados/disponiveis", headers=h_aluno)
    assert r.status_code == 200, r.text
    assert [s["id"] for s in r.json()["dados"]] == [sid]


def test_gestor_nao_tem_disponiveis(client, h_gestor):
    r = client.get("/simulados/disponiveis", headers=h_gestor)
    assert r.status_code == 403
    assert r.json()["codigo"] == "nao_e_aluno"


def test_monitoramento_progresso_por_aluno(client, h_gestor, h_aluno, dados):
    sid = _cria(client, h_gestor, dados["turma_id"], quantidade=3)
    _gerar(client, h_gestor, sid)
    _liberar(client, h_gestor, sid)
    # um aluno responde 1 das 3 questões
    qa = client.get(f"/simulados/{sid}/questoes", headers=h_aluno).json()["questoes"]
    alvo = qa[0]
    client.post(
        "/respostas",
        headers=h_aluno,
        json={
            "simulado_id": sid,
            "questao_id": alvo["questao_id"],
            "alternativa_id": alvo["alternativas"][0]["alternativa_id"],
        },
    )
    mon = client.get(f"/simulados/{sid}/monitoramento", headers=h_gestor).json()
    assert mon["total_alunos"] == 2  # conftest: 2 alunos na turma
    assert mon["total_questoes"] == 3
    assert mon["em_andamento"] == 1
    assert mon["nao_iniciaram"] == 1
    assert len(mon["por_aluno"]) == 2
    assert any(
        a["respondidas"] == 1 and a["situacao"] == "em_andamento"
        for a in mon["por_aluno"]
    )


def test_usuarios_inclui_aluno_id(client, h_gestor, dados):
    r = client.get(
        f"/usuarios?perfil=aluno&turma_id={dados['turma_id']}", headers=h_gestor
    )
    assert r.status_code == 200
    alunos = r.json()["dados"]
    assert alunos and all(u["aluno_id"] is not None for u in alunos)
