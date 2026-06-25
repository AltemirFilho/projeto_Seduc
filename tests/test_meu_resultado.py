import pytest
from sqlalchemy import select

from app.enums import StatusSimulado
from app.models import Aluno, Questao, Resposta, Simulado, SimuladoQuestao, Usuario


@pytest.fixture()
def simulado_respondido(Sessao, dados):
    """Simulado LIBERADO com 2 questões; o aluno acerta a 1ª e erra a 2ª."""
    with Sessao() as s:
        aluno_usuario = s.scalars(
            select(Usuario).where(Usuario.email == "aluno@x.gov.br")
        ).one()
        aluno = s.scalars(
            select(Aluno).where(Aluno.usuario_id == aluno_usuario.id)
        ).one()
        qs = list(s.scalars(select(Questao).order_by(Questao.id)))[:2]

        sim = Simulado(
            gestor_id=dados["gestor_id"],
            turma_id=dados["turma_id"],
            titulo="Simulado 1",
            status=StatusSimulado.LIBERADO,
        )
        s.add(sim)
        s.flush()
        for ordem, q in enumerate(qs, start=1):
            s.add(
                SimuladoQuestao(
                    simulado_id=sim.id,
                    questao_id=q.id,
                    ordem_questao=ordem,
                    alternativas_ordem=[a.id for a in q.alternativas],
                )
            )

        q1, q2 = qs
        certa1 = next(a for a in q1.alternativas if a.correta)
        errada2 = next(a for a in q2.alternativas if not a.correta)
        s.add(
            Resposta(
                aluno_id=aluno.id,
                simulado_id=sim.id,
                questao_id=q1.id,
                alternativa_id=certa1.id,
                correta=True,
            )
        )
        s.add(
            Resposta(
                aluno_id=aluno.id,
                simulado_id=sim.id,
                questao_id=q2.id,
                alternativa_id=errada2.id,
                correta=False,
            )
        )
        s.commit()
        return sim.id


def test_meu_resultado_aluno(client, h_aluno, simulado_respondido):
    sid = simulado_respondido
    r = client.get(f"/simulados/{sid}/meu-resultado", headers=h_aluno)
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["simulado"]["id"] == sid
    assert c["total_questoes"] == 2
    assert c["respondidas"] == 2
    assert c["acertos"] == 1
    assert c["erros"] == 1
    assert c["percentual_acerto"] == 0.5

    qs = c["questoes"]
    assert len(qs) == 2
    certa = [q for q in qs if q["acertou"]][0]
    errada = [q for q in qs if not q["acertou"]][0]
    assert certa["sua_resposta"] == certa["gabarito"]
    assert errada["sua_resposta"] != errada["gabarito"]
    assert errada["gabarito"]


def test_meu_resultado_sem_respostas(client, h_aluno2, simulado_respondido):
    # aluno2 está na turma mas não respondeu: vê o próprio resultado vazio
    r = client.get(f"/simulados/{simulado_respondido}/meu-resultado", headers=h_aluno2)
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["respondidas"] == 0
    assert c["acertos"] == 0
    assert c["questoes"] == []


def test_meu_resultado_gestor_barrado(client, h_gestor, simulado_respondido):
    r = client.get(f"/simulados/{simulado_respondido}/meu-resultado", headers=h_gestor)
    assert r.status_code == 403


def test_meu_resultado_anonimo_barrado(client, simulado_respondido):
    r = client.get(f"/simulados/{simulado_respondido}/meu-resultado")
    assert r.status_code in (401, 403)


def test_meu_resultado_simulado_inexistente(client, h_aluno):
    r = client.get("/simulados/99999/meu-resultado", headers=h_aluno)
    assert r.status_code == 404
