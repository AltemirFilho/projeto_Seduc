from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_gestor
from app.models import Questao
from app.repositories import questao_repository
from app.services import questao_service

router = APIRouter(prefix="/questoes", tags=["questoes"])


class AlternativaIn(BaseModel):
    texto: str
    correta: bool = False


class CadastrarQuestaoRequest(BaseModel):
    enunciado: str = Field(..., examples=["Qual é a raiz de 2x - 8 = 0?"])
    serie: str = Field(..., examples=["9º ano"])
    materia: str = Field(..., examples=["Matemática"])
    conteudo: str = Field(..., examples=["Funções"])
    nivel: str = Field(..., examples=["Fácil"])
    adaptacoes: list[str] = []
    alternativas: list[AlternativaIn]


class EditarQuestaoRequest(BaseModel):
    """Edição parcial: só os campos enviados são alterados."""

    enunciado: str | None = None
    serie: str | None = None
    materia: str | None = None
    conteudo: str | None = None
    nivel: str | None = None
    adaptacoes: list[str] | None = None
    imagem_url: str | None = None
    alternativas: list[AlternativaIn] | None = None


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


@router.get(
    "",
    summary="Listar e filtrar questões do banco (paginado)",
    dependencies=[Depends(require_gestor)],
)
def listar_questoes(
    serie: str | None = Query(None, description="Ex.: '9º ano'"),
    materia: str | None = Query(None, description="Ex.: 'Matemática'"),
    conteudo: str | None = Query(None, description="Ex.: 'Funções'"),
    nivel: str | None = Query(None, description="Fácil, Médio ou Difícil"),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    sessao: Session = Depends(get_session),
) -> dict:
    itens, total = questao_repository.buscar_paginado(
        sessao,
        serie=serie,
        materia=materia,
        conteudo=conteudo,
        nivel=nivel,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    return {
        "dados": [_serializar(q) for q in itens],
        "meta": {
            "pagina": pagina,
            "porPagina": por_pagina,
            "total": total,
            "totalPaginas": total_paginas,
        },
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar uma questão",
    dependencies=[Depends(require_gestor)],
)
def cadastrar_questao(
    req: CadastrarQuestaoRequest, sessao: Session = Depends(get_session)
) -> dict:
    questao = questao_service.cadastrar_questao(
        sessao,
        enunciado=req.enunciado,
        serie=req.serie,
        materia=req.materia,
        conteudo=req.conteudo,
        nivel=req.nivel,
        alternativas=[a.model_dump() for a in req.alternativas],
        adaptacoes=req.adaptacoes,
    )
    return _serializar(questao)


@router.get(
    "/{questao_id}",
    summary="Ver uma questão pelo id (gestor)",
    dependencies=[Depends(require_gestor)],
)
def obter_questao(questao_id: int, sessao: Session = Depends(get_session)) -> dict:
    return _serializar(questao_service.obter_questao(sessao, questao_id))


@router.patch(
    "/{questao_id}",
    summary="Editar uma questão (gestor)",
    dependencies=[Depends(require_gestor)],
)
def editar_questao(
    questao_id: int,
    req: EditarQuestaoRequest,
    sessao: Session = Depends(get_session),
) -> dict:
    questao = questao_service.editar_questao(
        sessao,
        questao_id=questao_id,
        enunciado=req.enunciado,
        serie=req.serie,
        materia=req.materia,
        conteudo=req.conteudo,
        nivel=req.nivel,
        adaptacoes=req.adaptacoes,
        imagem_url=req.imagem_url,
        alternativas=(
            [a.model_dump() for a in req.alternativas]
            if req.alternativas is not None
            else None
        ),
    )
    return _serializar(questao)
