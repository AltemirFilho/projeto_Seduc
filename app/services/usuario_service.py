from __future__ import annotations

from sqlalchemy.orm import Session

from app.enums import PerfilUsuario
from app.exceptions import (
    DadosInvalidos,
    NaoEncontrado,
    PermissaoNegada,
    RegraNegocio,
)
from app.models import Aluno, Usuario
from app.repositories import turma_repository, usuario_repository
from app.services import auth_service

SENHA_MINIMA = 6


def _perfil_de(valor: str) -> PerfilUsuario:
    try:
        return PerfilUsuario(valor)
    except ValueError as exc:
        validos = ", ".join(p.value for p in PerfilUsuario)
        raise DadosInvalidos(
            f"perfil inválido: '{valor}'. Use um de: {validos}"
        ) from exc


def criar_usuario(
    sessao: Session,
    *,
    nome: str,
    email: str,
    senha: str,
    perfil: str,
    solicitante: Usuario,
    turma_id: int | None = None,
) -> Usuario:
    nome = (nome or "").strip()
    email = (email or "").strip().lower()
    if not nome:
        raise DadosInvalidos("nome é obrigatório")
    if not email:
        raise DadosInvalidos("email é obrigatório")
    if not senha or len(senha) < SENHA_MINIMA:
        raise DadosInvalidos(f"a senha deve ter ao menos {SENHA_MINIMA} caracteres")

    perfil_obj = _perfil_de(perfil)

    # Teto de privilégio: ninguém cria um ADMIN além de outro ADMIN (evita um gestor
    # escalar para o tier que tem passe livre em todo o isolamento).
    if perfil_obj == PerfilUsuario.ADMIN and solicitante.perfil != PerfilUsuario.ADMIN:
        raise PermissaoNegada(
            "apenas um admin pode criar outro admin", codigo="perfil_acima_do_seu"
        )

    if usuario_repository.buscar_por_email(sessao, email) is not None:
        raise RegraNegocio("já existe um usuário com este email", codigo="email_em_uso")

    if perfil_obj == PerfilUsuario.ALUNO:
        if turma_id is None:
            raise DadosInvalidos("aluno precisa de uma turma (turma_id)")
        if turma_repository.buscar_por_id(sessao, turma_id) is None:
            raise NaoEncontrado(f"turma {turma_id} não encontrada")

    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=auth_service.gerar_hash_senha(senha),
        perfil=perfil_obj,
    )
    sessao.add(usuario)
    sessao.flush()
    if perfil_obj == PerfilUsuario.ALUNO:
        sessao.add(Aluno(usuario=usuario, turma_id=turma_id, perfil_cognitivo=[]))
    sessao.commit()
    sessao.refresh(usuario)
    return usuario


def listar_usuarios(
    sessao: Session, *, perfil: str | None = None, turma_id: int | None = None
) -> list[Usuario]:
    perfil_obj = _perfil_de(perfil) if perfil else None
    return usuario_repository.listar(sessao, perfil=perfil_obj, turma_id=turma_id)
