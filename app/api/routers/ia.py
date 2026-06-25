from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.services import predicao_service

router = APIRouter(prefix="/ia", tags=["ia"])


@router.get(
    "/risco/{aluno_id}",
    summary="Risco de evasão do aluno: calcula, salva e devolve (gestor)",
    dependencies=[Depends(require_gestor)],
)
def risco_do_aluno(aluno_id: int, sessao: Session = Depends(get_session)) -> dict:
    predicao = predicao_service.calcular_risco(sessao, aluno_id=aluno_id)
    return {
        "aluno_id": predicao.aluno_id,
        "score_risco": predicao.score_risco,
        "classificacao": predicao.classificacao,
        "fatores": predicao.fatores,
        "modelo_versao": predicao.modelo_versao,
        "calculada_em": (
            predicao.calculada_em.isoformat() if predicao.calculada_em else None
        ),
    }
