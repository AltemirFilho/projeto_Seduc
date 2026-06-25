def _id_primeira_questao(client, headers):
    r = client.get("/questoes", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()["dados"][0]["id"]


def test_obter_questao_gestor(client, h_gestor):
    qid = _id_primeira_questao(client, h_gestor)
    r = client.get(f"/questoes/{qid}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["id"] == qid
    assert "enunciado" in corpo
    assert sum(a["correta"] for a in corpo["alternativas"]) == 1


def test_obter_questao_aluno_barrado(client, h_aluno):
    # GET de questão expõe o gabarito ('correta') -> restrito a gestor/admin
    assert client.get("/questoes/1", headers=h_aluno).status_code == 403


def test_obter_questao_inexistente(client, h_gestor):
    r = client.get("/questoes/99999", headers=h_gestor)
    assert r.status_code == 404
    assert r.json()["codigo"] == "nao_encontrado"


def test_editar_enunciado(client, h_gestor):
    qid = _id_primeira_questao(client, h_gestor)
    r = client.patch(
        f"/questoes/{qid}", headers=h_gestor, json={"enunciado": "Quanto é 2+2?"}
    )
    assert r.status_code == 200, r.text
    assert r.json()["enunciado"] == "Quanto é 2+2?"
    # persistiu
    novo = client.get(f"/questoes/{qid}", headers=h_gestor).json()
    assert novo["enunciado"] == "Quanto é 2+2?"


def test_editar_nivel(client, h_gestor):
    qid = _id_primeira_questao(client, h_gestor)
    r = client.patch(f"/questoes/{qid}", headers=h_gestor, json={"nivel": "Difícil"})
    assert r.status_code == 200, r.text
    assert r.json()["nivel"] == "Difícil"


def test_editar_substitui_alternativas(client, h_gestor):
    qid = _id_primeira_questao(client, h_gestor)
    payload = {
        "alternativas": [
            {"texto": "10", "correta": True},
            {"texto": "20", "correta": False},
            {"texto": "30", "correta": False},
        ]
    }
    r = client.patch(f"/questoes/{qid}", headers=h_gestor, json=payload)
    assert r.status_code == 200, r.text
    alts = r.json()["alternativas"]
    assert [a["texto"] for a in alts] == ["10", "20", "30"]
    assert sum(a["correta"] for a in alts) == 1


def test_editar_alternativas_sem_correta_e_422(client, h_gestor):
    qid = _id_primeira_questao(client, h_gestor)
    r = client.patch(
        f"/questoes/{qid}",
        headers=h_gestor,
        json={"alternativas": [{"texto": "a"}, {"texto": "b"}]},
    )
    assert r.status_code == 422
    assert r.json()["codigo"] == "dados_invalidos"


def test_editar_troca_materia_sem_conteudo_e_422(client, h_gestor):
    qid = _id_primeira_questao(client, h_gestor)
    r = client.patch(f"/questoes/{qid}", headers=h_gestor, json={"materia": "História"})
    assert r.status_code == 422


def test_editar_aluno_barrado(client, h_aluno):
    r = client.patch("/questoes/1", headers=h_aluno, json={"enunciado": "x"})
    assert r.status_code == 403


def test_editar_questao_inexistente(client, h_gestor):
    r = client.patch("/questoes/99999", headers=h_gestor, json={"enunciado": "x"})
    assert r.status_code == 404
