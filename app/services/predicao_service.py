"""Predição de risco de evasão (Frente B / IA).

Regra de negócio: junta as features do aluno a partir das respostas e dos simulados da
turma, chama o `ml_service` (scikit-learn) e persiste/atualiza a previsão mais recente.
As queries ficam no `predicao_repository`; o modelo, no `ml_service`.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import StatusSimulado
from app.exceptions import NaoEncontrado
from app.integrations import ml_service
from app.models import Aluno, PredicaoRisco
from app.repositories import predicao_repository


def _features(sessao: Session, aluno: Aluno) -> dict | None:
    """Features do aluno, ou None quando não há simulados avaliáveis (dados insuficientes)."""
    avaliaveis = predicao_repository.simulados_avaliaveis_da_turma(
        sessao, aluno.turma_id
    )
    if not avaliaveis:
        return None

    respostas = predicao_repository.respostas_do_aluno(sessao, aluno.id)
    respondidas = len(respostas)
    acertos = sum(1 for r in respostas if r.correta)
    taxa_acerto = acertos / respondidas if respondidas else 0.0

    ids_respondidos = {r.simulado_id for r in respostas}
    ids_avaliaveis = {s.id for s in avaliaveis}
    taxa_participacao = len(ids_respondidos & ids_avaliaveis) / len(ids_avaliaveis)

    # Média de nota nos simulados FINALIZADOS em que o aluno participou.
    acertos_por_sim: dict[int, int] = {}
    for r in respostas:
        if r.correta:
            acertos_por_sim[r.simulado_id] = acertos_por_sim.get(r.simulado_id, 0) + 1
    notas: list[float] = []
    for s in avaliaveis:
        if s.status == StatusSimulado.FINALIZADO and s.id in ids_respondidos:
            total = len(s.questoes)
            if total:
                notas.append(10 * acertos_por_sim.get(s.id, 0) / total)
    # Sem prova finalizada ainda: aproxima pela taxa de acerto (0 se nunca respondeu).
    media_nota = sum(notas) / len(notas) if notas else taxa_acerto * 10

    return {
        "media_nota": media_nota,
        "taxa_participacao": taxa_participacao,
        "taxa_acerto": taxa_acerto,
    }


def calcular_risco(sessao: Session, *, aluno_id: int) -> PredicaoRisco:
    aluno = sessao.get(Aluno, aluno_id)
    if aluno is None:
        raise NaoEncontrado(f"aluno {aluno_id} não encontrado")

    features = _features(sessao, aluno)
    if features is None:
        resultado = {
            "score_risco": 0.0,
            "classificacao": "indeterminado",
            "fatores": ["dados insuficientes: turma ainda sem simulados avaliados"],
        }
        modelo_versao = "indeterminado"
    else:
        resultado = ml_service.prever(**features)
        modelo_versao = ml_service.MODELO_VERSAO

    predicao = sessao.scalar(
        select(PredicaoRisco).where(PredicaoRisco.aluno_id == aluno_id)
    )
    if predicao is None:
        predicao = PredicaoRisco(aluno_id=aluno_id)
        sessao.add(predicao)
    predicao.score_risco = resultado["score_risco"]
    predicao.classificacao = resultado["classificacao"]
    predicao.fatores = resultado["fatores"]
    predicao.modelo_versao = modelo_versao

    sessao.commit()
    sessao.refresh(predicao)
    return predicao
