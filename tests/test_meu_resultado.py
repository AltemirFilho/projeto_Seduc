import pytest
from sqlalchemy import select

from app.enums import StatusSimulado
from app.models import (
    Aluno,
    Escola,
    Questao,
    Resposta,
    Serie,
    Simulado,
    SimuladoQuestao,
    Turma,
    Usuario,
)


def _aluno_por_email(s, email):
    u = s.scalars(select(Usuario).where(Usuario.email == email)).one()
    return s.scalars(select(Aluno).where(Aluno.usuario_id == u.id)).one()


def _cria_simulado(s, *, gestor_id, turma_id, status, questoes):
    sim = Simulado(
        gestor_id=gestor_id, turma_id=turma_id, titulo="Simulado", status=status
    )
    s.add(sim)
    s.flush()
    for ordem, q in enumerate(questoes, start=1):
        s.add(
            SimuladoQuestao(
                simulado_id=sim.id,
                questao_id=q.id,
                ordem_questao=ordem,
                alternativas_ordem=[a.id for a in q.alternativas],
            )
        )
    return sim


def _responde(s, *, aluno, simulado, questao, correta):
    alt = (
        next(a for a in questao.alternativas if a.correta)
        if correta
        else next(a for a in questao.alternativas if not a.correta)
    )
    s.add(
        Resposta(
            aluno_id=aluno.id,
            simulado_id=simulado.id,
            questao_id=questao.id,
            alternativa_id=alt.id,
            correta=correta,
        )
    )


@pytest.fixture()
def finalizado(Sessao, dados):
    """Simulado FINALIZADO; o aluno acerta a 1ª questão e erra a 2ª."""
    with Sessao() as s:
        aluno = _aluno_por_email(s, "aluno@x.gov.br")
        qs = list(s.scalars(select(Questao).order_by(Questao.id)))[:2]
        sim = _cria_simulado(
            s,
            gestor_id=dados["gestor_id"],
            turma_id=dados["turma_id"],
            status=StatusSimulado.FINALIZADO,
            questoes=qs,
        )
        _responde(s, aluno=aluno, simulado=sim, questao=qs[0], correta=True)
        _responde(s, aluno=aluno, simulado=sim, questao=qs[1], correta=False)
        s.commit()
        return sim.id


def test_meu_resultado_aluno(client, h_aluno, finalizado):
    r = client.get(f"/simulados/{finalizado}/meu-resultado", headers=h_aluno)
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["total_questoes"] == 2
    assert c["respondidas"] == 2
    assert c["acertos"] == 1
    assert c["erros"] == 1
    qs = c["questoes"]
    certa = [q for q in qs if q["acertou"]][0]
    errada = [q for q in qs if not q["acertou"]][0]
    assert certa["sua_resposta"] == certa["gabarito"]
    assert errada["sua_resposta"] != errada["gabarito"]
    assert errada["gabarito"]


def test_meu_resultado_sem_respostas(client, h_aluno2, finalizado):
    r = client.get(f"/simulados/{finalizado}/meu-resultado", headers=h_aluno2)
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["respondidas"] == 0
    assert c["acertos"] == 0
    assert c["questoes"] == []


def test_meu_resultado_prova_aberta_nao_revela_gabarito(client, h_aluno, Sessao, dados):
    # Simulado LIBERADO (prova em andamento): resultado bloqueado, gabarito oculto.
    with Sessao() as s:
        aluno = _aluno_por_email(s, "aluno@x.gov.br")
        qs = list(s.scalars(select(Questao).order_by(Questao.id)))[:1]
        sim = _cria_simulado(
            s,
            gestor_id=dados["gestor_id"],
            turma_id=dados["turma_id"],
            status=StatusSimulado.LIBERADO,
            questoes=qs,
        )
        _responde(s, aluno=aluno, simulado=sim, questao=qs[0], correta=True)
        s.commit()
        sid = sim.id
    r = client.get(f"/simulados/{sid}/meu-resultado", headers=h_aluno)
    assert r.status_code == 409
    assert r.json()["codigo"] == "simulado_nao_finalizado"
    assert "gabarito" not in r.text


def test_meu_resultado_outra_turma_404(client, h_aluno, Sessao, dados):
    # Simulado de OUTRA turma: nem título/status devem vazar -> 404.
    with Sessao() as s:
        serie = s.scalars(select(Serie)).first()
        escola2 = Escola(nome="Escola 2")
        turma2 = Turma(escola=escola2, serie=serie, ano_letivo=2026, nome="9B")
        s.add_all([escola2, turma2])
        s.flush()
        qs = list(s.scalars(select(Questao).order_by(Questao.id)))[:1]
        sim = _cria_simulado(
            s,
            gestor_id=dados["gestor_id"],
            turma_id=turma2.id,
            status=StatusSimulado.FINALIZADO,
            questoes=qs,
        )
        s.commit()
        sid = sim.id
    r = client.get(f"/simulados/{sid}/meu-resultado", headers=h_aluno)
    assert r.status_code == 404


def test_meu_resultado_gestor_barrado(client, h_gestor, finalizado):
    r = client.get(f"/simulados/{finalizado}/meu-resultado", headers=h_gestor)
    assert r.status_code == 403


def test_meu_resultado_anonimo_barrado(client, finalizado):
    r = client.get(f"/simulados/{finalizado}/meu-resultado")
    assert r.status_code in (401, 403)


def test_meu_resultado_simulado_inexistente(client, h_aluno):
    r = client.get("/simulados/99999/meu-resultado", headers=h_aluno)
    assert r.status_code == 404
