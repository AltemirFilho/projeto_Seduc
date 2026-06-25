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


def gestor_tem_simulado_na_turma(
    sessao: Session, *, gestor_id: int, turma_id: int
) -> bool:
    """Vínculo do gestor com a turma, derivado sem schema novo: o gestor é responsável
    pela turma se já criou algum simulado nela (qualquer status)."""
    stmt = (
        select(Simulado.id)
        .where(Simulado.gestor_id == gestor_id, Simulado.turma_id == turma_id)
        .limit(1)
    )
    return sessao.scalar(stmt) is not None


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
