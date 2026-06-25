from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.enums import PerfilUsuario
from app.models import Aluno, Usuario


def buscar_por_email(sessao: Session, email: str) -> Usuario | None:
    # Normaliza para login e cadastro baterem mesmo com diferença de caixa/espaços.
    alvo = (email or "").strip().lower()
    return sessao.scalar(select(Usuario).where(Usuario.email == alvo))


def buscar_por_id(sessao: Session, usuario_id: int) -> Usuario | None:
    return sessao.get(Usuario, usuario_id)


def aluno_do_usuario(sessao: Session, usuario_id: int) -> Aluno | None:
    return sessao.scalar(select(Aluno).where(Aluno.usuario_id == usuario_id))


def listar(
    sessao: Session,
    *,
    turma_id: int | None = None,
    perfil: PerfilUsuario | None = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> tuple[list[Usuario], int]:
    stmt = select(Usuario).options(selectinload(Usuario.aluno))
    if turma_id is not None:
        stmt = stmt.join(Aluno, Aluno.usuario_id == Usuario.id).where(
            Aluno.turma_id == turma_id
        )
    if perfil is not None:
        stmt = stmt.where(Usuario.perfil == perfil)
    todos = list(sessao.scalars(stmt.order_by(Usuario.id)).unique())
    total = len(todos)
    inicio = (pagina - 1) * por_pagina
    return todos[inicio : inicio + por_pagina], total
