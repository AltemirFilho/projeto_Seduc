from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.enums import StatusSimulado
from app.models import Resposta, Simulado


def respostas_do_aluno(sessao: Session, aluno_id: int) -> list[Resposta]:
    return list(
        sessao.scalars(
            select(Resposta).where(Resposta.aluno_id == aluno_id)
        ).all()
    )


def simulados_avaliaveis_da_turma(sessao: Session, turma_id: int) -> list[Simulado]:
    """Simulados que já foram oportunidade real de participação (liberados ou
    finalizados), com as questões carregadas para contar o total de cada um."""
    stmt = (
        select(Simulado)
        .where(
            Simulado.turma_id == turma_id,
            Simulado.status.in_(
                [StatusSimulado.LIBERADO, StatusSimulado.FINALIZADO]
            ),
        )
        .options(selectinload(Simulado.questoes))
    )
    return list(sessao.scalars(stmt).unique().all())
