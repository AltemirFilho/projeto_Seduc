from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.enums import PerfilUsuario
from app.exceptions import DadosInvalidos, NaoEncontrado, RegraNegocio
from app.models import Aluno, Usuario
from app.repositories import turma_repository, usuario_repository
from app.services import auth_service

SENHA_MINIMA = 6


def _parse_perfil(valor: str) -> PerfilUsuario:
    try:
        return PerfilUsuario(valor)
    except ValueError:
        permitidos = ", ".join(p.value for p in PerfilUsuario)
        raise DadosInvalidos(f"perfil inválido: '{valor}' (use: {permitidos})")


def criar_usuario(
    sessao: Session,
    *,
    nome: str,
    email: str,
    senha: str,
    perfil: str,
    turma_id: int | None = None,
) -> Usuario:
    nome = (nome or "").strip()
    email = (email or "").strip().lower()
    if not nome:
        raise DadosInvalidos("nome é obrigatório")
    if "@" not in email:
        raise DadosInvalidos("e-mail inválido")
    if len(senha or "") < SENHA_MINIMA:
        raise DadosInvalidos(f"a senha deve ter ao menos {SENHA_MINIMA} caracteres")

    perfil_enum = _parse_perfil(perfil)

    if usuario_repository.buscar_por_email(sessao, email) is not None:
        raise RegraNegocio("e-mail já cadastrado", codigo="email_em_uso")

    # Aluno só existe vinculado a uma turma válida.
    if perfil_enum is PerfilUsuario.ALUNO:
        if turma_id is None:
            raise DadosInvalidos("aluno exige turma_id")
        if turma_repository.buscar_por_id(sessao, turma_id) is None:
            raise NaoEncontrado(f"turma {turma_id} não encontrada")

    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=auth_service.gerar_hash_senha(senha),
        perfil=perfil_enum,
    )
    sessao.add(usuario)
    try:
        sessao.flush()
        if perfil_enum is PerfilUsuario.ALUNO:
            sessao.add(
                Aluno(usuario_id=usuario.id, turma_id=turma_id, perfil_cognitivo=[])
            )
        sessao.commit()
    except IntegrityError as exc:
        # Backstop de corrida: o pré-check passou, mas o unique do banco barrou.
        sessao.rollback()
        raise RegraNegocio("e-mail já cadastrado", codigo="email_em_uso") from exc

    sessao.refresh(usuario)
    return usuario


def listar_usuarios(
    sessao: Session,
    *,
    turma_id: int | None = None,
    perfil: str | None = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> tuple[list[Usuario], int]:
    perfil_enum = _parse_perfil(perfil) if perfil else None
    return usuario_repository.listar(
        sessao,
        turma_id=turma_id,
        perfil=perfil_enum,
        pagina=pagina,
        por_pagina=por_pagina,
    )
