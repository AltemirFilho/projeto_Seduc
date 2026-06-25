def _criar(client, headers, **body):
    return client.post("/usuarios", headers=headers, json=body)


def test_criar_aluno_vinculado_a_turma(client, h_gestor, dados):
    r = _criar(
        client,
        h_gestor,
        nome="Novo Aluno",
        email="novo@aluno.se.gov.br",
        senha="senha123",
        perfil="aluno",
        turma_id=dados["turma_id"],
    )
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["perfil"] == "aluno"
    assert corpo["turma_id"] == dados["turma_id"]
    assert "senha_hash" not in corpo


def test_criar_gestor_sem_turma(client, h_gestor):
    r = _criar(
        client,
        h_gestor,
        nome="Nova Gestora",
        email="nova@gestao.se.gov.br",
        senha="senha123",
        perfil="gestor",
    )
    assert r.status_code == 201, r.text
    assert r.json()["perfil"] == "gestor"
    assert r.json()["turma_id"] is None


def test_criar_email_duplicado_409(client, h_gestor):
    r = _criar(
        client,
        h_gestor,
        nome="Repetido",
        email="gestor@x.gov.br",  # já existe na fixture
        senha="senha123",
        perfil="gestor",
    )
    assert r.status_code == 409
    assert r.json()["codigo"] == "email_em_uso"


def test_criar_aluno_sem_turma_422(client, h_gestor):
    r = _criar(
        client,
        h_gestor,
        nome="Sem Turma",
        email="semturma@aluno.se.gov.br",
        senha="senha123",
        perfil="aluno",
    )
    assert r.status_code == 422


def test_criar_perfil_invalido_422(client, h_gestor):
    r = _criar(
        client,
        h_gestor,
        nome="X",
        email="x@y.gov.br",
        senha="senha123",
        perfil="rei",
    )
    assert r.status_code == 422


def test_criar_turma_inexistente_404(client, h_gestor):
    r = _criar(
        client,
        h_gestor,
        nome="X",
        email="x2@y.gov.br",
        senha="senha123",
        perfil="aluno",
        turma_id=99999,
    )
    assert r.status_code == 404


def test_listar_alunos_da_turma(client, h_gestor, dados):
    r = client.get(
        "/usuarios", headers=h_gestor, params={"turma_id": dados["turma_id"]}
    )
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert "dados" in corpo and "meta" in corpo
    assert corpo["meta"]["total"] >= 2  # a fixture cria 2 alunos na turma
    assert all(u["perfil"] == "aluno" for u in corpo["dados"])


def test_listar_filtra_por_perfil(client, h_gestor):
    r = client.get("/usuarios", headers=h_gestor, params={"perfil": "gestor"})
    assert r.status_code == 200, r.text
    assert all(u["perfil"] == "gestor" for u in r.json()["dados"])


def test_aluno_barrado(client, h_aluno, dados):
    assert client.get("/usuarios", headers=h_aluno).status_code == 403
    r = _criar(
        client, h_aluno, nome="X", email="x3@y.gov.br", senha="senha123", perfil="gestor"
    )
    assert r.status_code == 403


def test_anonimo_barrado(client):
    assert client.get("/usuarios").status_code in (401, 403)
