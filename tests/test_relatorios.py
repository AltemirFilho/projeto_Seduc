import pytest
from sqlalchemy import select

from app.enums import StatusSimulado
from app.models import (
    Alternativa,
    Aluno,
    Conteudo,
    Materia,
    Nivel,
    Questao,
    Resposta,
    Serie,
    Simulado,
)


def _questao(serie, materia, conteudo, nivel, enunciado):
    return Questao(
        enunciado=enunciado,
        serie=serie,
        materia=materia,
        conteudo=conteudo,
        nivel=nivel,
        adaptacoes=[],
        alternativas=[
            Alternativa(texto="certa", correta=True, ordem_original=1),
            Alternativa(texto="errada", correta=False, ordem_original=2),
        ],
    )


@pytest.fixture()
def relatorio(Sessao, dados):
    """Simulado da turma com respostas em 2 conteúdos de taxa de erro distinta:
    'Teste' (1 erro em 4 = 25%) e 'Geometria' (3 erros em 4 = 75%)."""
    turma_id = dados["turma_id"]
    with Sessao() as s:
        serie = s.scalars(select(Serie)).first()
        materia = s.scalars(select(Materia).where(Materia.nome == "Matemática")).one()
        nivel = s.scalars(select(Nivel)).first()
        conteudo_teste = s.scalars(
            select(Conteudo).where(Conteudo.nome == "Teste")
        ).one()
        alunos = list(
            s.scalars(
                select(Aluno).where(Aluno.turma_id == turma_id).order_by(Aluno.id)
            )
        )
        t1, t2 = list(
            s.scalars(
                select(Questao)
                .where(Questao.conteudo_id == conteudo_teste.id)
                .order_by(Questao.id)
            )
        )[:2]

        geometria = Conteudo(nome="Geometria", materia=materia)
        s.add(geometria)
        s.flush()
        g1 = _questao(serie, materia, geometria, nivel, "Área do quadrado?")
        g2 = _questao(serie, materia, geometria, nivel, "Soma dos ângulos?")
        s.add_all([g1, g2])

        simulado = Simulado(
            gestor_id=dados["gestor_id"],
            turma_id=turma_id,
            titulo="Simulado 1",
            status=StatusSimulado.LIBERADO,
        )
        s.add(simulado)
        s.flush()

        a, b = alunos[0], alunos[1]

        def resp(aluno, questao, correta):
            return Resposta(
                aluno_id=aluno.id,
                simulado_id=simulado.id,
                questao_id=questao.id,
                alternativa_id=questao.alternativas[0].id,
                correta=correta,
            )

        s.add_all(
            [
                # Teste: 3 acertos, 1 erro → 25%
                resp(a, t1, True),
                resp(a, t2, True),
                resp(b, t1, True),
                resp(b, t2, False),
                # Geometria: 1 acerto, 3 erros → 75%
                resp(a, g1, False),
                resp(a, g2, False),
                resp(b, g1, True),
                resp(b, g2, False),
            ]
        )
        s.commit()


def test_relatorio_turma_gestor(client, h_gestor, dados, relatorio):
    r = client.get(f"/relatorios/turma/{dados['turma_id']}", headers=h_gestor)
    assert r.status_code == 200, r.text
    corpo = r.json()

    assert corpo["turma"]["nome"] == "9A"
    assert corpo["total_alunos"] == 2
    assert corpo["total_respostas"] == 8
    assert corpo["total_acertos"] == 4
    assert corpo["media_acerto"] == 0.5

    ranking = corpo["conteudos"]
    assert [c["conteudo"] for c in ranking] == ["Geometria", "Teste"]
    assert ranking[0]["taxa_erro"] == 0.75
    assert ranking[0]["erros"] == 3
    assert ranking[1]["taxa_erro"] == 0.25


def test_relatorio_turma_aluno_barrado(client, h_aluno, dados, relatorio):
    r = client.get(f"/relatorios/turma/{dados['turma_id']}", headers=h_aluno)
    assert r.status_code == 403


def test_relatorio_turma_anonimo_barrado(client, dados):
    r = client.get(f"/relatorios/turma/{dados['turma_id']}")
    assert r.status_code in (401, 403)


def test_relatorio_turma_inexistente(client, h_gestor):
    r = client.get("/relatorios/turma/99999", headers=h_gestor)
    assert r.status_code == 404
    assert r.json()["codigo"] == "nao_encontrado"


def test_relatorio_turma_sem_respostas(client, h_gestor, dados):
    # Turma existe mas sem nenhuma resposta: 200 com zeros (guard de divisão por zero).
    r = client.get(f"/relatorios/turma/{dados['turma_id']}", headers=h_gestor)
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["total_respostas"] == 0
    assert c["total_acertos"] == 0
    assert c["media_acerto"] == 0.0
    assert c["conteudos"] == []
    assert c["total_alunos"] == 2
