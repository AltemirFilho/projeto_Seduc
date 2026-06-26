from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.models import Usuario
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


class CriarUsuarioRequest(BaseModel):
    nome: str = Field(..., examples=["Ana Beatriz Souza"])
    email: str = Field(..., examples=["ana@sedu.se.gov.br"])
    senha: str = Field(..., min_length=6)
    perfil: str = Field("aluno", examples=["aluno"])
    turma_id: int | None = Field(None, description="Obrigatório quando perfil = aluno")


def _serializar(usuario: Usuario) -> dict:
    return {
        "id": usuario.id,
        # aluno_id é o id usado pelos endpoints de aluno (ex.: /ia/risco/{aluno_id}),
        # que difere do usuario.id; expor aqui evita o cliente confundir os dois.
        "aluno_id": usuario.aluno.id if usuario.aluno else None,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil.value,
        "turma_id": usuario.aluno.turma_id if usuario.aluno else None,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário e vincular aluno à turma (gestor/admin)",
)
def criar_usuario(
    req: CriarUsuarioRequest,
    solicitante: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    usuario = usuario_service.criar_usuario(
        sessao,
        nome=req.nome,
        email=req.email,
        senha=req.senha,
        perfil=req.perfil,
        solicitante=solicitante,
        turma_id=req.turma_id,
    )
    return _serializar(usuario)


@router.get(
    "",
    summary="Listar usuários, com filtro por perfil e turma (gestor/admin)",
    dependencies=[Depends(require_gestor)],
)
def listar_usuarios(
    perfil: str | None = Query(None, description="admin, gestor, aluno ou suporte"),
    turma_id: int | None = Query(None),
    sessao: Session = Depends(get_session),
) -> dict:
    usuarios = usuario_service.listar_usuarios(
        sessao, perfil=perfil, turma_id=turma_id
    )
    return {
        "dados": [_serializar(u) for u in usuarios],
        "meta": {"total": len(usuarios)},
    }
