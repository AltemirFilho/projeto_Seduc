from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.enums import StatusSimulado
from app.models import Aluno, Questao, Resposta, ResultadoSimulado, Simulado


def respostas_da_turma(sessao: Session, turma_id: int) -> list[Resposta]:
    """Respostas dos simulados FINALIZADOS de uma turma, com a questão e o conteúdo
    carregados (para agregar taxa de erro por conteúdo sem N+1)."""
    stmt = (
        select(Resposta)
        .join(Simulado, Resposta.simulado_id == Simulado.id)
        .where(
            Simulado.turma_id == turma_id,
            Simulado.status == StatusSimulado.FINALIZADO,
        )
        .options(selectinload(Resposta.questao).selectinload(Questao.conteudo))
    )
    return list(sessao.scalars(stmt).unique().all())


def resultados_da_turma(sessao: Session, turma_id: int) -> list[ResultadoSimulado]:
    """Resultados persistidos (correção) dos simulados de uma turma."""
    stmt = (
        select(ResultadoSimulado)
        .join(Simulado, ResultadoSimulado.simulado_id == Simulado.id)
        .where(Simulado.turma_id == turma_id)
    )
    return list(sessao.scalars(stmt).all())


def contar_alunos_da_turma(sessao: Session, turma_id: int) -> int:
    return (
        sessao.scalar(select(func.count(Aluno.id)).where(Aluno.turma_id == turma_id))
        or 0
    )


def resultado_do_aluno(
    sessao: Session, *, aluno_id: int, simulado_id: int
) -> ResultadoSimulado | None:
    return sessao.scalar(
        select(ResultadoSimulado).where(
            ResultadoSimulado.aluno_id == aluno_id,
            ResultadoSimulado.simulado_id == simulado_id,
        )
    )


def respostas_do_aluno_no_simulado(
    sessao: Session, *, aluno_id: int, simulado_id: int
) -> list[Resposta]:
    return list(
        sessao.scalars(
            select(Resposta).where(
                Resposta.aluno_id == aluno_id,
                Resposta.simulado_id == simulado_id,
            )
        ).all()
    )
