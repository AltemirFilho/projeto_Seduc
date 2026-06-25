from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.enums import PerfilUsuario
from app.models import Aluno, Usuario


def buscar_por_email(sessao: Session, email: str) -> Usuario | None:
    return sessao.scalar(select(Usuario).where(Usuario.email == email))


def listar(
    sessao: Session,
    *,
    perfil: PerfilUsuario | None = None,
    turma_id: int | None = None,
) -> list[Usuario]:
    stmt = select(Usuario).options(selectinload(Usuario.aluno)).order_by(Usuario.id)
    if perfil is not None:
        stmt = stmt.where(Usuario.perfil == perfil)
    if turma_id is not None:
        stmt = stmt.join(Aluno, Aluno.usuario_id == Usuario.id).where(
            Aluno.turma_id == turma_id
        )
    return list(sessao.scalars(stmt).unique().all())


def buscar_por_id(sessao: Session, usuario_id: int) -> Usuario | None:
    return sessao.get(Usuario, usuario_id)


def aluno_do_usuario(sessao: Session, usuario_id: int) -> Aluno | None:
    return sessao.scalar(select(Aluno).where(Aluno.usuario_id == usuario_id))
