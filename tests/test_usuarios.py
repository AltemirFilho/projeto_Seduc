"""Testes do cadastro/listagem de usuários (Épico 2)."""


def _login(client, email, senha="sedu123"):
    r = client.post("/auth/login", json={"email": email, "senha": senha})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_gestor_nao_cria_admin(client, h_gestor):
    # Escalonamento de privilégio barrado: gestor não promove ninguém a admin.
    r = client.post(
        "/usuarios",
        headers=h_gestor,
        json={"nome": "X", "email": "viraadmin@x.gov.br", "senha": "sedu123", "perfil": "admin"},
    )
    assert r.status_code == 403
    assert r.json()["codigo"] == "perfil_acima_do_seu"


def test_admin_cria_admin(client):
    h = _login(client, "admin@x.gov.br")
    r = client.post(
        "/usuarios",
        headers=h,
        json={"nome": "Admin 2", "email": "admin2@x.gov.br", "senha": "sedu123", "perfil": "admin"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["perfil"] == "admin"


def test_gestor_cria_aluno_vinculado_a_turma(client, h_gestor, dados):
    r = client.post(
        "/usuarios",
        headers=h_gestor,
        json={
            "nome": "Novo Aluno",
            "email": "novo@x.gov.br",
            "senha": "sedu123",
            "perfil": "aluno",
            "turma_id": dados["turma_id"],
        },
    )
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["perfil"] == "aluno"
    assert corpo["turma_id"] == dados["turma_id"]
    # o usuário criado consegue logar
    login = client.post(
        "/auth/login", json={"email": "novo@x.gov.br", "senha": "sedu123"}
    )
    assert login.status_code == 200


def test_email_duplicado_409(client, h_gestor):
    j = {"nome": "A", "email": "dup@x.gov.br", "senha": "sedu123", "perfil": "gestor"}
    assert client.post("/usuarios", headers=h_gestor, json=j).status_code == 201
    r = client.post("/usuarios", headers=h_gestor, json=j)
    assert r.status_code == 409
    assert r.json()["codigo"] == "email_em_uso"


def test_aluno_sem_turma_422(client, h_gestor):
    r = client.post(
        "/usuarios",
        headers=h_gestor,
        json={"nome": "X", "email": "semturma@x.gov.br", "senha": "sedu123", "perfil": "aluno"},
    )
    assert r.status_code == 422


def test_perfil_invalido_422(client, h_gestor):
    r = client.post(
        "/usuarios",
        headers=h_gestor,
        json={"nome": "X", "email": "z@x.gov.br", "senha": "sedu123", "perfil": "diretor"},
    )
    assert r.status_code == 422


def test_aluno_nao_cria_usuario(client, h_aluno, dados):
    r = client.post(
        "/usuarios",
        headers=h_aluno,
        json={
            "nome": "X",
            "email": "y@x.gov.br",
            "senha": "sedu123",
            "perfil": "aluno",
            "turma_id": dados["turma_id"],
        },
    )
    assert r.status_code == 403


def test_listar_filtra_por_perfil_e_turma(client, h_gestor, dados):
    r = client.get(
        f"/usuarios?perfil=aluno&turma_id={dados['turma_id']}", headers=h_gestor
    )
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["meta"]["total"] == 2  # os 2 alunos do conftest
    assert all(u["perfil"] == "aluno" for u in corpo["dados"])
    assert all(u["turma_id"] == dados["turma_id"] for u in corpo["dados"])
