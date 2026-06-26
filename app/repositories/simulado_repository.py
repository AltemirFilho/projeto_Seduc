from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.enums import StatusSimulado
from app.models import Simulado


def listar(
    sessao: Session,
    *,
    gestor_id: Optional[int] = None,
    turma_id: Optional[int] = None,
    status: Optional[StatusSimulado] = None,
    statuses: Optional[Sequence[StatusSimulado]] = None,
) -> list[Simulado]:
    """Lista simulados com filtros opcionais (mais recentes primeiro).

    `gestor_id` restringe ao dono (gestão vê os seus; admin passa None p/ ver todos).
    `turma_id` restringe à turma (lista do aluno). `status` filtra um estado; `statuses`
    filtra um conjunto (ex.: liberados + finalizados, p/ a visão do aluno).
    """
    stmt = (
        select(Simulado)
        .options(selectinload(Simulado.questoes), selectinload(Simulado.turma))
        .order_by(Simulado.criado_em.desc(), Simulado.id.desc())
    )
    if gestor_id is not None:
        stmt = stmt.where(Simulado.gestor_id == gestor_id)
    if turma_id is not None:
        stmt = stmt.where(Simulado.turma_id == turma_id)
    if status is not None:
        stmt = stmt.where(Simulado.status == status)
    if statuses:
        stmt = stmt.where(Simulado.status.in_(list(statuses)))
    return list(sessao.scalars(stmt).unique().all())
