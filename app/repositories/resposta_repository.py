from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Aluno, Conteudo, Materia, Questao, Resposta, Simulado


def _acertos():
    # Soma de respostas corretas, portável: avg(boolean) é recusado pelo Postgres,
    # então contamos via case(...) em vez de tirar média direto da coluna booleana.
    return func.coalesce(func.sum(case((Resposta.correta, 1), else_=0)), 0)


def contar_alunos_turma(sessao: Session, turma_id: int) -> int:
    return (
        sessao.scalar(select(func.count(Aluno.id)).where(Aluno.turma_id == turma_id))
        or 0
    )


def estatisticas_turma(sessao: Session, turma_id: int) -> tuple[int, int]:
    """(total_respostas, total_acertos) das respostas de simulados da turma."""
    stmt = (
        select(func.count(Resposta.id), _acertos())
        .join(Simulado, Resposta.simulado_id == Simulado.id)
        .where(Simulado.turma_id == turma_id)
    )
    total, acertos = sessao.execute(stmt).one()
    return int(total or 0), int(acertos or 0)


def desempenho_por_conteudo(
    sessao: Session, turma_id: int
) -> list[tuple[str, str, int, int]]:
    """Por conteúdo da turma: (conteudo, materia, total_respostas, acertos)."""
    stmt = (
        select(
            Conteudo.nome,
            Materia.nome,
            func.count(Resposta.id),
            _acertos(),
        )
        .join(Simulado, Resposta.simulado_id == Simulado.id)
        .join(Questao, Resposta.questao_id == Questao.id)
        .join(Conteudo, Questao.conteudo_id == Conteudo.id)
        .join(Materia, Questao.materia_id == Materia.id)
        .where(Simulado.turma_id == turma_id)
        .group_by(Conteudo.id, Conteudo.nome, Materia.nome)
    )
    return [
        (conteudo, materia, int(total), int(acertos))
        for conteudo, materia, total, acertos in sessao.execute(stmt).all()
    ]
