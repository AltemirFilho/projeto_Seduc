from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.models import Usuario
from app.services import diagnostico_service, predicao_service

router = APIRouter(prefix="/ia", tags=["ia"])


@router.get(
    "/risco/{aluno_id}",
    summary="Risco de evasão do aluno: calcula, salva e devolve (gestor da turma)",
)
def risco_do_aluno(
    aluno_id: int,
    solicitante: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    predicao = predicao_service.calcular_risco(
        sessao, aluno_id=aluno_id, solicitante=solicitante
    )
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


@router.get(
    "/diagnostico/{simulado_id}",
    summary="Diagnóstico pedagógico da turma num simulado finalizado (gestor dono)",
)
def diagnostico_da_turma(
    simulado_id: int,
    solicitante: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    diagnostico = diagnostico_service.gerar_diagnostico(
        sessao, simulado_id=simulado_id, solicitante=solicitante
    )
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
