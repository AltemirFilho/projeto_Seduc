"""Testes da predição de risco de evasão (Frente B / IA)."""

from sqlalchemy import select

from app.models import Aluno, Usuario


def _aluno_id(Sessao, email):
    with Sessao() as s:
        usuario = s.scalar(select(Usuario).where(Usuario.email == email))
        aluno = s.scalar(select(Aluno).where(Aluno.usuario_id == usuario.id))
        return aluno.id


def _simulado_liberado(client, h_gestor, turma_id, quantidade=3):
    r = client.post(
        "/simulados",
        headers=h_gestor,
        json={
            "turma_id": turma_id,
            "titulo": "Simulado risco",
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
    return sid


def _responde_tudo_certo(client, h_gestor, h_aluno, sid):
    preview = client.get(f"/simulados/{sid}/preview", headers=h_gestor).json()["questoes"]
    for q in preview:
        correta = next(a for a in q["alternativas"] if a["correta"])
        r = client.post(
            "/respostas",
            headers=h_aluno,
            json={
                "simulado_id": sid,
                "questao_id": q["questao_id"],
                "alternativa_id": correta["alternativa_id"],
            },
        )
        assert r.status_code == 200, r.text


def test_risco_indeterminado_sem_simulados(client, h_gestor, dados, Sessao):
    # Turma ainda sem simulados liberados/finalizados: não dá para prever.
    aluno_id = _aluno_id(Sessao, "aluno@x.gov.br")
    r = client.get(f"/ia/risco/{aluno_id}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["classificacao"] == "indeterminado"
    assert corpo["modelo_versao"] == "indeterminado"
    assert any("insuficientes" in f for f in corpo["fatores"])


def test_risco_baixo_aluno_engajado(client, h_gestor, h_aluno, dados, Sessao):
    sid = _simulado_liberado(client, h_gestor, dados["turma_id"])
    _responde_tudo_certo(client, h_gestor, h_aluno, sid)
    client.post(f"/simulados/{sid}/finalizar", headers=h_gestor, json={})

    aluno_id = _aluno_id(Sessao, "aluno@x.gov.br")
    r = client.get(f"/ia/risco/{aluno_id}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["classificacao"] == "baixo"
    assert corpo["modelo_versao"] == "logreg-v1"
    assert 0.0 <= corpo["score_risco"] < 0.34
    assert corpo["fatores"] == ["sem fatores de risco relevantes"]


def test_risco_alto_aluno_sem_participacao(client, h_gestor, h_aluno, dados, Sessao):
    # Só o aluno 1 responde; o aluno 2 fica de fora -> participação 0 -> alto risco.
    sid = _simulado_liberado(client, h_gestor, dados["turma_id"])
    _responde_tudo_certo(client, h_gestor, h_aluno, sid)
    client.post(f"/simulados/{sid}/finalizar", headers=h_gestor, json={})

    aluno2_id = _aluno_id(Sessao, "aluno2@x.gov.br")
    r = client.get(f"/ia/risco/{aluno2_id}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["classificacao"] == "alto"
    assert corpo["score_risco"] >= 0.67
    assert any("participação" in f for f in corpo["fatores"])


def test_risco_exige_gestor(client, h_aluno, dados, Sessao):
    aluno_id = _aluno_id(Sessao, "aluno@x.gov.br")
    r = client.get(f"/ia/risco/{aluno_id}", headers=h_aluno)
    assert r.status_code == 403


def test_risco_aluno_inexistente(client, h_gestor):
    r = client.get("/ia/risco/99999", headers=h_gestor)
    assert r.status_code == 404


def test_fatores_sempre_coerentes_com_classificacao():
    # A explicabilidade nunca pode contradizer o risco: risco != baixo => há fatores.
    from app.integrations import ml_service

    valores = [i / 10 for i in range(11)]  # 0.0 .. 1.0
    for participacao in valores:
        for acerto in valores:
            r = ml_service.prever(
                media_nota=acerto * 10,
                taxa_participacao=participacao,
                taxa_acerto=acerto,
            )
            if r["classificacao"] != "baixo":
                assert r["fatores"] != ["sem fatores de risco relevantes"], (
                    participacao,
                    acerto,
                    r,
                )
