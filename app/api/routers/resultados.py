from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_perfis
from app.enums import PerfilUsuario
from app.models import Usuario
from app.services import resultado_service

router = APIRouter(prefix="/simulados", tags=["resultados"])


@router.get(
    "/{simulado_id}/meu-resultado",
    summary="Resultado do aluno autenticado no simulado (nota, erros e gabarito)",
)
def meu_resultado(
    simulado_id: int,
    usuario: Usuario = Depends(require_perfis(PerfilUsuario.ALUNO)),
    sessao: Session = Depends(get_session),
) -> dict:
    return resultado_service.meu_resultado(
        sessao, usuario_id=usuario.id, simulado_id=simulado_id
    )
