"""Endpoints de QUESTÕES: listar e filtrar o banco de questões.

Corresponde ao GET /questoes do backlog. A busca é delegada ao repositório.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.models import Questao
from app.repositories import questao_repository

router = APIRouter(prefix="/questoes", tags=["questoes"])


def _serializar(questao: Questao) -> dict:
    return {
        "id": questao.id,
        "enunciado": questao.enunciado,
        "serie": questao.serie.nome,
        "materia": questao.materia.nome,
        "conteudo": questao.conteudo.nome,
        "nivel": questao.nivel.nome,
        "adaptacoes": questao.adaptacoes,
        "alternativas": [
            {
                "id": alt.id,
                "texto": alt.texto,
                "correta": alt.correta,
                "ordem_original": alt.ordem_original,
            }
            for alt in questao.alternativas
        ],
    }


@router.get("")
def listar_questoes(
    serie: str | None = Query(None, description="Ex.: '9º ano'"),
    materia: str | None = Query(None, description="Ex.: 'Matemática'"),
    conteudo: str | None = Query(None, description="Ex.: 'Funções'"),
    nivel: str | None = Query(None, description="Fácil, Médio ou Difícil"),
    limite: int = Query(20, ge=1, le=200),
    sessao: Session = Depends(get_session),
) -> list[dict]:
    """Lista questões aplicando filtros opcionais por etiqueta."""
    questoes = questao_repository.filtrar_questoes(
        sessao,
        serie=serie,
        materia=materia,
        conteudos=[conteudo] if conteudo else None,
        nivel=nivel,
        limite=limite,
    )
    return [_serializar(q) for q in questoes]
