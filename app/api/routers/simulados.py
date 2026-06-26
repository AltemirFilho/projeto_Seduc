from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_session, obter_usuario_atual, require_gestor
from app.exceptions import PermissaoNegada
from app.models import Usuario
from app.repositories import usuario_repository
from app.services import relatorio_service, simulado_service

router = APIRouter(prefix="/simulados", tags=["simulados"])


class CriarSimuladoRequest(BaseModel):
    turma_id: int
    titulo: str = Field(..., examples=["Simulado de Matemática - 9º ano"])
    serie: str = Field(..., examples=["9º ano"])
    materia: str | None = Field(None, examples=["Matemática"])
    materias: list[str] | None = Field(None, examples=[["Matemática", "Português"]])
    conteudos: list[str] | None = None
    distribuicao: dict[str, float] | None = Field(
        None, examples=[{"Fácil": 0.3, "Médio": 0.5, "Difícil": 0.2}]
    )
    quantidade: int = Field(10, ge=1, le=100)
    adaptacoes: list[str] | None = None
    seed: int | None = None


class GerarRequest(BaseModel):
    seed: int | None = Field(None, description="Fixa o sorteio (reproduzível)")


def _resumo(simulado) -> dict:
    return {
        "id": simulado.id,
        "titulo": simulado.titulo,
        "status": simulado.status.value,
        "turma_id": simulado.turma_id,
        "turma": simulado.turma.nome if simulado.turma else None,
        "gestor_id": simulado.gestor_id,
        "total_questoes": len(simulado.questoes),
        "criado_em": simulado.criado_em.isoformat() if simulado.criado_em else None,
        "parametros": simulado.parametros_json,
    }


@router.get("", summary="Listar simulados (gestão: filtra por status e turma)")
def listar_simulados(
    estado: str | None = Query(
        None, alias="status", description="rascunho, gerado, liberado ou finalizado"
    ),
    turma_id: int | None = Query(None),
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    simulados = simulado_service.listar_para_gestor(
        sessao, solicitante=usuario, status=estado, turma_id=turma_id
    )
    return {"dados": [_resumo(s) for s in simulados], "meta": {"total": len(simulados)}}


@router.get(
    "/disponiveis",
    summary="Simulados liberados/finalizados da turma do aluno autenticado",
)
def simulados_disponiveis(
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(get_session),
) -> dict:
    simulados = simulado_service.listar_do_aluno(sessao, solicitante=usuario)
    return {"dados": [_resumo(s) for s in simulados], "meta": {"total": len(simulados)}}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Criar simulado (gestor)")
def criar_simulado(
    req: CriarSimuladoRequest,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    parametros = {
        "serie": req.serie,
        "materia": req.materia,
        "materias": req.materias,
        "conteudos": req.conteudos,
        "distribuicao": req.distribuicao,
        "quantidade": req.quantidade,
        "adaptacoes": req.adaptacoes,
        "seed": req.seed,
    }
    simulado = simulado_service.criar_simulado(
        sessao,
        gestor_id=usuario.id,
        turma_id=req.turma_id,
        titulo=req.titulo,
        parametros=parametros,
    )
    return _resumo(simulado)


@router.post("/{simulado_id}/gerar", summary="Gerar e persistir as questões (gestor)")
def gerar(
    simulado_id: int,
    req: GerarRequest,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    simulado = simulado_service.gerar_e_persistir(
        sessao, simulado_id=simulado_id, solicitante=usuario, seed=req.seed
    )
    return _resumo(simulado)


@router.get("/{simulado_id}/preview", summary="Prévia COM gabarito (gestor dono)")
def preview(
    simulado_id: int,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    questoes = simulado_service.montar_questoes_preview(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )
    return {"simulado_id": simulado_id, "questoes": questoes}


@router.post("/{simulado_id}/liberar", summary="Liberar para os alunos (gestor dono)")
def liberar(
    simulado_id: int,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    simulado = simulado_service.liberar(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )
    return _resumo(simulado)


@router.get(
    "/{simulado_id}/questoes",
    summary="Questões do simulado SEM gabarito (visão do aluno da turma)",
)
def questoes_do_aluno(
    simulado_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(get_session),
) -> dict:
    questoes = simulado_service.montar_questoes_do_aluno(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )
    return {"simulado_id": simulado_id, "questoes": questoes}


@router.get(
    "/{simulado_id}/meu-resultado",
    summary="Resultado individual do próprio aluno (nota, acertos e gabarito)",
)
def meu_resultado(
    simulado_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(get_session),
) -> dict:
    aluno = usuario_repository.aluno_do_usuario(sessao, usuario.id)
    if aluno is None:
        raise PermissaoNegada(
            "apenas alunos têm resultado individual", codigo="nao_e_aluno"
        )
    return relatorio_service.meu_resultado(
        sessao, simulado_id=simulado_id, aluno=aluno
    )


@router.post("/{simulado_id}/finalizar", summary="Finalizar e corrigir (gestor dono)")
def finalizar(
    simulado_id: int,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    return simulado_service.finalizar_e_corrigir(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )


@router.delete(
    "/{simulado_id}/questoes/{questao_id}",
    summary="Remover uma questão do simulado (gestor dono, antes de liberar)",
)
def remover_questao(
    simulado_id: int,
    questao_id: int,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    simulado_service.remover_questao(
        sessao, simulado_id=simulado_id, questao_id=questao_id, solicitante=usuario
    )
    questoes = simulado_service.montar_questoes_preview(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )
    return {"simulado_id": simulado_id, "questoes": questoes}


@router.post(
    "/{simulado_id}/questoes/{questao_id}/trocar",
    summary="Trocar uma questão por outra equivalente (gestor dono, antes de liberar)",
)
def trocar_questao(
    simulado_id: int,
    questao_id: int,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    simulado_service.trocar_questao(
        sessao, simulado_id=simulado_id, questao_id=questao_id, solicitante=usuario
    )
    questoes = simulado_service.montar_questoes_preview(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )
    return {"simulado_id": simulado_id, "questoes": questoes}


# NOTA: declarado depois de "/disponiveis" para não capturar a rota literal como id.
@router.get("/{simulado_id}", summary="Resumo de um simulado (gestor dono)")
def obter_simulado(
    simulado_id: int,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    simulado = simulado_service.obter_resumo(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )
    return _resumo(simulado)


@router.get(
    "/{simulado_id}/monitoramento",
    summary="Progresso ao vivo da turma no simulado (gestor dono)",
)
def monitorar_simulado(
    simulado_id: int,
    usuario: Usuario = Depends(require_gestor),
    sessao: Session = Depends(get_session),
) -> dict:
    return simulado_service.monitorar(
        sessao, simulado_id=simulado_id, solicitante=usuario
    )
