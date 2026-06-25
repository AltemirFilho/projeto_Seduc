"""Testes de ver e editar uma questão (Épico 3)."""


def _cria_questao(client, h_gestor):
    r = client.post(
        "/questoes",
        headers=h_gestor,
        json={
            "enunciado": "2+2?",
            "serie": "9º ano",
            "materia": "Matemática",
            "conteudo": "Soma",
            "nivel": "Fácil",
            "alternativas": [
                {"texto": "4", "correta": True},
                {"texto": "5", "correta": False},
            ],
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_ver_questao(client, h_gestor):
    qid = _cria_questao(client, h_gestor)
    r = client.get(f"/questoes/{qid}", headers=h_gestor)
    assert r.status_code == 200
    assert r.json()["id"] == qid
    assert r.json()["enunciado"] == "2+2?"


def test_ver_questao_inexistente_404(client, h_gestor):
    assert client.get("/questoes/99999", headers=h_gestor).status_code == 404


def test_editar_enunciado(client, h_gestor):
    qid = _cria_questao(client, h_gestor)
    r = client.patch(
        f"/questoes/{qid}", headers=h_gestor, json={"enunciado": "Quanto é 2+2?"}
    )
    assert r.status_code == 200, r.text
    assert r.json()["enunciado"] == "Quanto é 2+2?"


def test_editar_alternativas(client, h_gestor):
    qid = _cria_questao(client, h_gestor)
    r = client.patch(
        f"/questoes/{qid}",
        headers=h_gestor,
        json={
            "alternativas": [
                {"texto": "4", "correta": True},
                {"texto": "6", "correta": False},
                {"texto": "8", "correta": False},
            ]
        },
    )
    assert r.status_code == 200, r.text
    assert len(r.json()["alternativas"]) == 3


def test_editar_alternativas_invalidas_422(client, h_gestor):
    qid = _cria_questao(client, h_gestor)
    # 6 alternativas excede o máximo
    r = client.patch(
        f"/questoes/{qid}",
        headers=h_gestor,
        json={"alternativas": [{"texto": str(i), "correta": i == 0} for i in range(6)]},
    )
    assert r.status_code == 422


def test_editar_nivel_inexistente_404(client, h_gestor):
    qid = _cria_questao(client, h_gestor)
    r = client.patch(f"/questoes/{qid}", headers=h_gestor, json={"nivel": "Impossível"})
    assert r.status_code == 404


def test_aluno_nao_ve_nem_edita(client, h_gestor, h_aluno):
    qid = _cria_questao(client, h_gestor)
    assert client.get(f"/questoes/{qid}", headers=h_aluno).status_code == 403
    assert (
        client.patch(
            f"/questoes/{qid}", headers=h_aluno, json={"enunciado": "x"}
        ).status_code
        == 403
    )
