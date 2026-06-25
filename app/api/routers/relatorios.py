from fastapi import APIRouter, Depends, Response
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


@router.get(
    "/turma/{turma_id}/csv",
    summary="Exportar o relatório da turma em CSV",
    dependencies=[Depends(require_gestor)],
)
def exportar_csv(turma_id: int, sessao: Session = Depends(get_session)) -> Response:
    dados = relatorio_service.relatorio_turma(sessao, turma_id)
    nome = f"relatorio_turma_{turma_id}.csv"
    return Response(
        content=relatorio_service.exportar_csv(dados),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.get(
    "/turma/{turma_id}/pdf",
    summary="Exportar o relatório da turma em PDF",
    dependencies=[Depends(require_gestor)],
)
def exportar_pdf(turma_id: int, sessao: Session = Depends(get_session)) -> Response:
    dados = relatorio_service.relatorio_turma(sessao, turma_id)
    nome = f"relatorio_turma_{turma_id}.pdf"
    return Response(
        content=relatorio_service.exportar_pdf(dados),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )
