from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.services import diagnostico_service

router = APIRouter(prefix="/ia", tags=["ia"])


@router.get(
    "/diagnostico/{simulado_id}",
    summary="Diagnóstico pedagógico da turma num simulado finalizado (gestor)",
    dependencies=[Depends(require_gestor)],
)
def diagnostico_da_turma(
    simulado_id: int, sessao: Session = Depends(get_session)
) -> dict:
    diagnostico = diagnostico_service.gerar_diagnostico(sessao, simulado_id=simulado_id)
    return {
        "simulado_id": diagnostico.simulado_id,
        "resumo": diagnostico.resumo,
        "pontos_fracos": diagnostico.pontos_fracos,
        "recomendacoes": diagnostico.recomendacoes,
        "modelo_versao": diagnostico.modelo_versao,
        "gerado_em": (
            diagnostico.gerado_em.isoformat() if diagnostico.gerado_em else None
        ),
    }
