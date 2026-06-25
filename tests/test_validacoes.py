import pytest

from app.exceptions import DadosInvalidos
from app.services import prova_service


def test_cadastro_seis_alternativas_rejeitado(client, h_gestor):
    r = client.post(
        "/questoes",
        headers=h_gestor,
        json={
            "enunciado": "x?",
            "serie": "9º ano",
            "materia": "Matemática",
            "conteudo": "Teste",
            "nivel": "Fácil",
            "alternativas": [{"texto": str(i), "correta": i == 0} for i in range(6)],
        },
    )
    assert r.status_code == 422
    assert r.json()["codigo"] == "dados_invalidos"


def test_cadastro_sem_correta_rejeitado(client, h_gestor):
    r = client.post(
        "/questoes",
        headers=h_gestor,
        json={
            "enunciado": "x?",
            "serie": "9º ano",
            "materia": "Matemática",
            "conteudo": "Teste",
            "nivel": "Fácil",
            "alternativas": [{"texto": "a", "correta": False}, {"texto": "b", "correta": False}],
        },
    )
    assert r.status_code == 422


def test_cadastro_valido_retorna_201(client, h_gestor):
    r = client.post(
        "/questoes",
        headers=h_gestor,
        json={
            "enunciado": "2+2?",
            "serie": "9º ano",
            "materia": "Matemática",
            "conteudo": "Soma",
            "nivel": "Fácil",
            "alternativas": [{"texto": "4", "correta": True}, {"texto": "5", "correta": False}],
        },
    )
    assert r.status_code == 201
    assert r.json()["id"]


def test_distribuicao_que_nao_soma_um_rejeitada(client, h_gestor):
    r = client.post(
        "/provas/gerar",
        headers=h_gestor,
        json={"serie": "9º ano", "materia": "Matemática", "distribuicao": {"Fácil": 0.5, "Médio": 0.2, "Difícil": 0.1}},
    )
    assert r.status_code == 422


def test_gerar_prova_traz_parametros_e_gabarito(client, h_gestor):
    r = client.post(
        "/provas/gerar",
        headers=h_gestor,
        json={"serie": "9º ano", "materia": "Matemática", "quantidade": 4, "seed": 1},
    )
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["parametros"]["quantidade"] == 4
    assert len(corpo["gabarito"]) == corpo["total"]


def test_liberar_antes_de_gerar_falha(client, h_gestor, dados):
    criar = client.post(
        "/simulados",
        headers=h_gestor,
        json={"turma_id": dados["turma_id"], "titulo": "x", "serie": "9º ano", "materia": "Matemática"},
    )
    sid = criar.json()["id"]
    r = client.post(f"/simulados/{sid}/liberar", headers=h_gestor, json={})
    assert r.status_code == 409


def test_finalizar_nao_liberado_falha(client, h_gestor, dados):
    criar = client.post(
        "/simulados",
        headers=h_gestor,
        json={"turma_id": dados["turma_id"], "titulo": "x", "serie": "9º ano", "materia": "Matemática", "quantidade": 3},
    )
    sid = criar.json()["id"]
    client.post(f"/simulados/{sid}/gerar", headers=h_gestor, json={})
    r = client.post(f"/simulados/{sid}/finalizar", headers=h_gestor, json={})
    assert r.status_code == 409


def test_distribuicao_nan_ou_infinito_rejeitada():
    # NaN/infinito passavam pela checagem de soma (NaN != NaN) e estouravam em round(NaN).
    with pytest.raises(DadosInvalidos):
        prova_service._validar_distribuicao({"Fácil": float("nan"), "Médio": 0.5})
    with pytest.raises(DadosInvalidos):
        prova_service._validar_distribuicao({"Fácil": float("inf")})


def test_distribuicao_nivel_desconhecido_rejeitada(client, h_gestor):
    # 'Facil' (sem acento) não casa com o nível 'Fácil' do banco: antes a prova saía
    # aleatória fingindo ser balanceada; agora falha claro (422).
    r = client.post(
        "/provas/gerar",
        headers=h_gestor,
        json={
            "serie": "9º ano",
            "materia": "Matemática",
            "distribuicao": {"Facil": 0.3, "Médio": 0.5, "Difícil": 0.2},
        },
    )
    assert r.status_code == 422
    assert r.json()["codigo"] == "dados_invalidos"


def test_quantidade_maior_que_o_banco_rejeitada(client, h_gestor):
    # O banco de teste tem 6 questões: pedir 50 deve falhar claro, não gerar prova curta.
    r = client.post(
        "/provas/gerar",
        headers=h_gestor,
        json={"serie": "9º ano", "materia": "Matemática", "quantidade": 50},
    )
    assert r.status_code == 409
    assert r.json()["codigo"] == "questoes_insuficientes"


def test_importacao_alternativa_malformada_nao_derruba_lote(client, h_gestor):
    # Alternativa que não é objeto antes virava AttributeError -> 500 no lote inteiro.
    # Agora é só uma linha rejeitada; as válidas entram.
    payload = {
        "questoes": [
            {
                "enunciado": "ok?",
                "etiquetas": {"serie": "9º ano", "materia": "Matemática", "conteudo": "Teste", "nivel": "Fácil"},
                "alternativas": [{"texto": "2", "correta": True}, {"texto": "3", "correta": False}],
            },
            {
                "enunciado": "malformada",
                "etiquetas": {"serie": "9º ano", "materia": "Matemática", "conteudo": "Teste", "nivel": "Fácil"},
                "alternativas": ["x = 2", "x = 4"],
            },
        ]
    }
    r = client.post("/questoes/import", headers=h_gestor, json=payload)
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["importadas"] == 1
    assert corpo["rejeitadas"] == 1
    assert corpo["erros"][0]["linha"] == 2


def test_importacao_relatorio_de_erros(client, h_gestor):
    payload = {
        "questoes": [
            {
                "enunciado": "ok?",
                "etiquetas": {"serie": "9º ano", "materia": "Matemática", "conteudo": "Teste", "nivel": "Fácil"},
                "alternativas": [{"texto": "2", "correta": True}, {"texto": "3", "correta": False}],
            },
            {
                "enunciado": "sem correta",
                "etiquetas": {"serie": "9º ano", "materia": "Matemática", "conteudo": "Teste", "nivel": "Fácil"},
                "alternativas": [{"texto": "2", "correta": False}, {"texto": "3", "correta": False}],
            },
        ]
    }
    r = client.post("/questoes/import", headers=h_gestor, json=payload)
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["importadas"] == 1
    assert corpo["rejeitadas"] == 1
    assert corpo["erros"][0]["linha"] == 2
