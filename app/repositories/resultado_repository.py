from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Questao, Resposta, Simulado, SimuladoQuestao


def buscar_simulado(sessao: Session, simulado_id: int) -> Simulado | None:
    return sessao.get(Simulado, simulado_id)


def contar_questoes_simulado(sessao: Session, simulado_id: int) -> int:
    return (
        sessao.scalar(
            select(func.count(SimuladoQuestao.id)).where(
                SimuladoQuestao.simulado_id == simulado_id
            )
        )
        or 0
    )


def respostas_do_aluno(
    sessao: Session, aluno_id: int, simulado_id: int
) -> list[Resposta]:
    stmt = (
        select(Resposta)
        .where(
            Resposta.aluno_id == aluno_id,
            Resposta.simulado_id == simulado_id,
        )
        .options(
            selectinload(Resposta.questao).selectinload(Questao.alternativas),
            selectinload(Resposta.alternativa),
        )
        .order_by(Resposta.questao_id)
    )
    return list(sessao.scalars(stmt).unique())
