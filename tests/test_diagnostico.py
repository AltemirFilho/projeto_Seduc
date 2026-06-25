"""Testes do diagnóstico pedagógico por IA (Frente B / IA).

A fixture autouse do conftest mantém a IA desligada, então os testes exercitam o
fallback (degrada aos dados crus); o caminho com IA é coberto via monkeypatch.
"""

from app.config import settings
from app.integrations import claude as claude_mod


def _simulado_finalizado(client, h_gestor, h_aluno, turma_id, *, acertar, quantidade=3):
    r = client.post(
        "/simulados",
        headers=h_gestor,
        json={
            "turma_id": turma_id,
            "titulo": "Simulado diag",
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

    preview = client.get(f"/simulados/{sid}/preview", headers=h_gestor).json()["questoes"]
    for q in preview:
        if acertar:
            alt = next(a for a in q["alternativas"] if a["correta"])
        else:
            alt = next(a for a in q["alternativas"] if not a["correta"])
        resp = client.post(
            "/respostas",
            headers=h_aluno,
            json={
                "simulado_id": sid,
                "questao_id": q["questao_id"],
                "alternativa_id": alt["alternativa_id"],
            },
        )
        assert resp.status_code == 200, resp.text
    client.post(f"/simulados/{sid}/finalizar", headers=h_gestor, json={})
    return sid


def test_diagnostico_fallback_sem_ia(client, h_gestor, h_aluno, dados):
    # IA desligada (autouse) -> degrada aos dados crus, com pontos fracos calculados.
    sid = _simulado_finalizado(client, h_gestor, h_aluno, dados["turma_id"], acertar=False)
    r = client.get(f"/ia/diagnostico/{sid}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["modelo_versao"] == "indisponivel"
    assert "Teste" in corpo["pontos_fracos"]  # conteúdo com 100% de erro
    assert corpo["resumo"]


def test_diagnostico_com_ia(client, h_gestor, h_aluno, dados, monkeypatch):
    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(
        claude_mod,
        "completar_json",
        lambda **kwargs: {
            "resumo": "A turma teve bom desempenho geral.",
            "pontos_fracos": ["Frações"],
            "recomendacoes": ["Revisar frações com exercícios dirigidos"],
        },
    )
    sid = _simulado_finalizado(client, h_gestor, h_aluno, dados["turma_id"], acertar=True)
    r = client.get(f"/ia/diagnostico/{sid}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["modelo_versao"] == settings.claude_modelo
    assert corpo["resumo"] == "A turma teve bom desempenho geral."
    assert corpo["recomendacoes"] == ["Revisar frações com exercícios dirigidos"]


def test_diagnostico_exige_finalizado(client, h_gestor, dados):
    # Simulado apenas gerado (não finalizado) não pode ser diagnosticado.
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
    rr = client.get(f"/ia/diagnostico/{sid}", headers=h_gestor)
    assert rr.status_code == 409


def test_diagnostico_exige_gestor(client, h_gestor, h_aluno, dados):
    sid = _simulado_finalizado(client, h_gestor, h_aluno, dados["turma_id"], acertar=True)
    r = client.get(f"/ia/diagnostico/{sid}", headers=h_aluno)
    assert r.status_code == 403


def test_diagnostico_simulado_inexistente(client, h_gestor):
    r = client.get("/ia/diagnostico/99999", headers=h_gestor)
    assert r.status_code == 404


def test_diagnostico_ia_listas_malformadas_viram_vazias(
    client, h_gestor, h_aluno, dados, monkeypatch
):
    # Se a IA devolver tipo errado nas listas, o serviço coage e não persiste lixo.
    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(
        claude_mod,
        "completar_json",
        lambda **kwargs: {"resumo": "ok", "pontos_fracos": "Frações", "recomendacoes": None},
    )
    sid = _simulado_finalizado(client, h_gestor, h_aluno, dados["turma_id"], acertar=True)
    r = client.get(f"/ia/diagnostico/{sid}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["resumo"] == "ok"
    assert corpo["pontos_fracos"] == []  # string -> coagida para lista vazia
    assert corpo["recomendacoes"] == []
