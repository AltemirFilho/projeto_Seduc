from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Questao, Resposta


def respostas_do_simulado(sessao: Session, simulado_id: int) -> list[Resposta]:
    """Respostas do simulado com a questão e o conteúdo carregados, para agregar a
    taxa de erro por conteúdo sem disparar lazy-load."""
    stmt = (
        select(Resposta)
        .where(Resposta.simulado_id == simulado_id)
        .options(selectinload(Resposta.questao).selectinload(Questao.conteudo))
    )
    return list(sessao.scalars(stmt).all())
