from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.services import relatorio_service

router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@router.get(
    "/turma/{turma_id}",
    summary="Relatório da turma: média, alunos e conteúdos por taxa de erro (gestor)",
    dependencies=[Depends(require_gestor)],
)
def relatorio_turma(turma_id: int, sessao: Session = Depends(get_session)) -> dict:
    return relatorio_service.relatorio_turma(sessao, turma_id=turma_id)


@router.get(
    "/turma/{turma_id}/export",
    summary="Exporta o relatório da turma em CSV ou PDF (gestor)",
    dependencies=[Depends(require_gestor)],
)
def exportar_turma(
    turma_id: int,
    formato: str = Query("csv", pattern="^(csv|pdf)$", description="csv ou pdf"),
    sessao: Session = Depends(get_session),
) -> Response:
    if formato == "pdf":
        conteudo = relatorio_service.exportar_turma_pdf(sessao, turma_id=turma_id)
        return Response(
            content=conteudo,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="relatorio_turma_{turma_id}.pdf"'
            },
        )
    texto = relatorio_service.exportar_turma_csv(sessao, turma_id=turma_id)
    return Response(
        content=texto.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="relatorio_turma_{turma_id}.csv"'
        },
    )
