"""Testes do isolamento por POSSE e por TURMA no ciclo do simulado.

Regra exercitada:
- o gestor opera apenas o simulado que criou (o admin tem bypass);
- o aluno só vê/responde simulado LIBERADO da própria turma.

O cenário base (uma turma, um gestor, dois alunos, um admin) vem do conftest; aqui criamos
um SEGUNDO gestor e uma SEGUNDA turma com aluno próprio para cruzar as fronteiras.
"""

import pytest
from sqlalchemy import select

from app.enums import PerfilUsuario
from app.models import Aluno, Escola, Serie, Turma, Usuario
from app.services import auth_service

SENHA = "sedu123"


@pytest.fixture()
def cenario_b(Sessao, dados):
    """Gestor B + turma B (outra escola) com um aluno próprio, na mesma série do conftest.

    Compartilha o banco em memória com a fixture `client` (StaticPool), então os registros
    criados aqui ficam visíveis para as requisições HTTP do teste.
    """
    with Sessao() as s:
        serie = s.scalar(select(Serie).where(Serie.nome == "9º ano"))
        gestor_b = Usuario(
            nome="Gestor B",
            email="gestorb@x.gov.br",
            senha_hash=auth_service.gerar_hash_senha(SENHA),
            perfil=PerfilUsuario.GESTOR,
        )
        u_aluno_b = Usuario(
            nome="Aluno B",
            email="alunob@x.gov.br",
            senha_hash=auth_service.gerar_hash_senha(SENHA),
            perfil=PerfilUsuario.ALUNO,
        )
        s.add_all([gestor_b, u_aluno_b])
        s.flush()
        escola_b = Escola(nome="Escola B", municipio="Aracaju")
        turma_b = Turma(escola=escola_b, serie=serie, ano_letivo=2026, nome="9B")
        s.add_all([escola_b, turma_b])
        s.flush()
        s.add(Aluno(usuario=u_aluno_b, turma=turma_b, perfil_cognitivo=[]))
        s.commit()
        return {"gestor_b_id": gestor_b.id, "turma_b_id": turma_b.id}


def _headers(client, email):
    r = client.post("/auth/login", json={"email": email, "senha": SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _cria_e_gera(client, headers, turma_id, quantidade=3):
    r = client.post(
        "/simulados",
        headers=headers,
        json={
            "turma_id": turma_id,
            "titulo": "Simulado A",
            "serie": "9º ano",
            "materia": "Matemática",
            "quantidade": quantidade,
            "seed": 7,
        },
    )
    assert r.status_code == 201, r.text
    sid = r.json()["id"]
    g = client.post(f"/simulados/{sid}/gerar", headers=headers, json={})
    assert g.status_code == 200, g.text
    return sid


def test_gestor_so_opera_o_proprio_simulado(client, h_gestor, dados, cenario_b):
    # Gestor A cria e gera; Gestor B é gestor (passa o require_gestor) mas não é o dono.
    sid = _cria_e_gera(client, h_gestor, dados["turma_id"])
    hb = _headers(client, "gestorb@x.gov.br")

    assert client.post(f"/simulados/{sid}/gerar", headers=hb, json={}).status_code == 403
    assert client.post(f"/simulados/{sid}/liberar", headers=hb, json={}).status_code == 403
    assert client.get(f"/simulados/{sid}/preview", headers=hb).status_code == 403
    assert client.post(f"/simulados/{sid}/finalizar", headers=hb, json={}).status_code == 403
    # A checagem de posse precede a busca da questão: o id da questão não influi na decisão
    # de acesso (por isso 403 mesmo com id inexistente).
    assert client.post(f"/simulados/{sid}/questoes/1/trocar", headers=hb).status_code == 403
    assert client.delete(f"/simulados/{sid}/questoes/1", headers=hb).status_code == 403


def test_posse_responde_codigo_nao_e_dono(client, h_gestor, dados, cenario_b):
    sid = _cria_e_gera(client, h_gestor, dados["turma_id"])
    hb = _headers(client, "gestorb@x.gov.br")
    r = client.post(f"/simulados/{sid}/liberar", headers=hb, json={})
    assert r.status_code == 403
    assert r.json()["codigo"] == "nao_e_dono"


def test_admin_opera_simulado_de_qualquer_gestor(client, h_gestor, dados):
    # Admin tem passe livre (bypass de posse) — documenta a regra de _exigir_dono.
    sid = _cria_e_gera(client, h_gestor, dados["turma_id"])
    ha = _headers(client, "admin@x.gov.br")
    r = client.post(f"/simulados/{sid}/liberar", headers=ha, json={})
    assert r.status_code == 200
    assert r.json()["status"] == "liberado"


def test_aluno_so_le_questoes_da_propria_turma(client, h_gestor, h_aluno, dados, cenario_b):
    sid = _cria_e_gera(client, h_gestor, dados["turma_id"])
    client.post(f"/simulados/{sid}/liberar", headers=h_gestor, json={})
    hb = _headers(client, "alunob@x.gov.br")

    r = client.get(f"/simulados/{sid}/questoes", headers=hb)
    assert r.status_code == 403
    assert r.json()["codigo"] == "fora_da_turma"
    # Controle: o aluno da turma A lê normalmente.
    assert client.get(f"/simulados/{sid}/questoes", headers=h_aluno).status_code == 200


def test_aluno_so_le_simulado_liberado(client, h_gestor, h_aluno, dados):
    # Apenas GERADO (ainda não liberado): o aluno da própria turma ainda não pode ver.
    sid = _cria_e_gera(client, h_gestor, dados["turma_id"])
    r = client.get(f"/simulados/{sid}/questoes", headers=h_aluno)
    assert r.status_code == 403
    assert r.json()["codigo"] == "simulado_nao_liberado"


def test_aluno_so_responde_simulado_da_propria_turma(client, h_gestor, dados, cenario_b):
    sid = _cria_e_gera(client, h_gestor, dados["turma_id"])
    client.post(f"/simulados/{sid}/liberar", headers=h_gestor, json={})
    # Questão vem do preview do dono (o aluno B nem consegue ler a visão do aluno).
    q = client.get(f"/simulados/{sid}/preview", headers=h_gestor).json()["questoes"][0]
    hb = _headers(client, "alunob@x.gov.br")
    r = client.post(
        "/respostas",
        headers=hb,
        json={
            "simulado_id": sid,
            "questao_id": q["questao_id"],
            "alternativa_id": q["alternativas"][0]["alternativa_id"],
        },
    )
    assert r.status_code == 403
    assert r.json()["codigo"] == "fora_da_turma"


# --- Isolamento dos endpoints de IA (mesma família: posse do simulado e turma do aluno) ---


def _simulado_finalizado(client, headers, h_aluno, turma_id):
    sid = _cria_e_gera(client, headers, turma_id)
    client.post(f"/simulados/{sid}/liberar", headers=headers, json={})
    prev = client.get(f"/simulados/{sid}/preview", headers=headers).json()["questoes"]
    for q in prev:
        alt = next(a for a in q["alternativas"] if a["correta"])
        client.post(
            "/respostas",
            headers=h_aluno,
            json={"simulado_id": sid, "questao_id": q["questao_id"], "alternativa_id": alt["alternativa_id"]},
        )
    client.post(f"/simulados/{sid}/finalizar", headers=headers, json={})
    return sid


def _aluno_id(Sessao, email):
    with Sessao() as s:
        usuario = s.scalar(select(Usuario).where(Usuario.email == email))
        aluno = s.scalar(select(Aluno).where(Aluno.usuario_id == usuario.id))
        return aluno.id


def test_diagnostico_so_do_gestor_dono(client, h_gestor, h_aluno, dados, cenario_b):
    sid = _simulado_finalizado(client, h_gestor, h_aluno, dados["turma_id"])
    hb = _headers(client, "gestorb@x.gov.br")
    assert client.get(f"/ia/diagnostico/{sid}", headers=hb).status_code == 403
    assert client.get(f"/ia/diagnostico/{sid}", headers=_headers(client, "admin@x.gov.br")).status_code == 200
    assert client.get(f"/ia/diagnostico/{sid}", headers=h_gestor).status_code == 200  # dono


def test_risco_so_de_aluno_de_turma_acompanhada(client, h_gestor, h_aluno, dados, cenario_b, Sessao):
    # Gestor A acompanha a turma A (tem simulado nela); Gestor B não.
    _simulado_finalizado(client, h_gestor, h_aluno, dados["turma_id"])
    aluno_a = _aluno_id(Sessao, "aluno@x.gov.br")
    hb = _headers(client, "gestorb@x.gov.br")
    r = client.get(f"/ia/risco/{aluno_a}", headers=hb)
    assert r.status_code == 403
    assert r.json()["codigo"] == "fora_da_turma"
    assert client.get(f"/ia/risco/{aluno_a}", headers=_headers(client, "admin@x.gov.br")).status_code == 200
    assert client.get(f"/ia/risco/{aluno_a}", headers=h_gestor).status_code == 200  # dono da turma
