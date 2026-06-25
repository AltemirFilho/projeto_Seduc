from __future__ import annotations

from sqlalchemy.orm import Session

from app.enums import StatusSimulado
from app.exceptions import NaoEncontrado, PermissaoNegada, RegraNegocio
from app.repositories import resultado_repository, usuario_repository


def _gabarito(questao) -> str | None:
    return next((alt.texto for alt in questao.alternativas if alt.correta), None)


def meu_resultado(sessao: Session, *, usuario_id: int, simulado_id: int) -> dict:
    """Resultado do próprio aluno num simulado: nota, acertos/erros e gabarito.
    A identidade do aluno vem do token (usuario_id), nunca do corpo/URL."""
    aluno = usuario_repository.aluno_do_usuario(sessao, usuario_id)
    if aluno is None:
        raise PermissaoNegada(
            "apenas alunos têm resultado de simulado", codigo="sem_perfil_aluno"
        )

    simulado = resultado_repository.buscar_simulado(sessao, simulado_id)
    if simulado is None or simulado.turma_id != aluno.turma_id:
        # Nao revela simulado de outra turma (404 em vez de vazar titulo/status).
        raise NaoEncontrado(f"simulado {simulado_id} não encontrado")
    if simulado.status is not StatusSimulado.FINALIZADO:
        # Gabarito/acerto so depois da correcao: impede o aluno de espiar o
        # gabarito (e corrigir respostas) com a prova ainda aberta (LIBERADO).
        raise RegraNegocio(
            "o resultado fica disponível após a finalização do simulado",
            codigo="simulado_nao_finalizado",
        )

    respostas = resultado_repository.respostas_do_aluno(sessao, aluno.id, simulado_id)
    total_questoes = resultado_repository.contar_questoes_simulado(sessao, simulado_id)
    acertos = sum(1 for r in respostas if r.correta)

    questoes = [
        {
            "questao_id": r.questao_id,
            "enunciado": r.questao.enunciado,
            "acertou": r.correta,
            "sua_resposta": r.alternativa.texto,
            "gabarito": _gabarito(r.questao),
        }
        for r in respostas
    ]

    return {
        "simulado": {
            "id": simulado.id,
            "titulo": simulado.titulo,
            "status": simulado.status.value,
        },
        "total_questoes": total_questoes,
        "respondidas": len(respostas),
        "acertos": acertos,
        "erros": len(respostas) - acertos,
        "percentual_acerto": (
            round(acertos / total_questoes, 4) if total_questoes else 0.0
        ),
        "questoes": questoes,
    }
