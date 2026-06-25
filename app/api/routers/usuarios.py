from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.models import Usuario
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


class CriarUsuarioRequest(BaseModel):
    nome: str = Field(..., examples=["Maria Aluna"])
    email: str = Field(..., examples=["maria@aluno.se.gov.br"])
    senha: str = Field(..., min_length=6)
    perfil: str = Field(
        ..., examples=["aluno"], description="aluno, gestor, admin ou suporte"
    )
    turma_id: int | None = Field(
        None, description="Obrigatório quando perfil = aluno"
    )


def _serializar(usuario: Usuario) -> dict:
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil.value,
        "ativo": usuario.ativo,
        "turma_id": usuario.aluno.turma_id if usuario.aluno else None,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário (aluno vinculado a turma, ou gestor/admin/suporte)",
    dependencies=[Depends(require_gestor)],
)
def criar_usuario(
    req: CriarUsuarioRequest, sessao: Session = Depends(get_session)
) -> dict:
    usuario = usuario_service.criar_usuario(
        sessao,
        nome=req.nome,
        email=req.email,
        senha=req.senha,
        perfil=req.perfil,
        turma_id=req.turma_id,
    )
    return _serializar(usuario)


@router.get(
    "",
    summary="Listar usuários (filtra por turma e/ou perfil; paginado)",
    dependencies=[Depends(require_gestor)],
)
def listar_usuarios(
    turma_id: int | None = Query(None, description="Filtra os alunos de uma turma"),
    perfil: str | None = Query(None, description="aluno, gestor, admin ou suporte"),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    sessao: Session = Depends(get_session),
) -> dict:
    itens, total = usuario_service.listar_usuarios(
        sessao, turma_id=turma_id, perfil=perfil, pagina=pagina, por_pagina=por_pagina
    )
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    return {
        "dados": [_serializar(u) for u in itens],
        "meta": {
            "pagina": pagina,
            "porPagina": por_pagina,
            "total": total,
            "totalPaginas": total_paginas,
        },
    }
