from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.services import relatorio_service

router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@router.get(
    "/turma/{turma_id}",
    summary="Relatório de desempenho da turma (média e conteúdos mais errados)",
    dependencies=[Depends(require_gestor)],
)
def relatorio_turma(turma_id: int, sessao: Session = Depends(get_session)) -> dict:
    return relatorio_service.relatorio_turma(sessao, turma_id)
