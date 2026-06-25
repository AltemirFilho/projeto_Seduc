"""Predição de risco de evasão (Frente B / IA).

Regra de negócio: junta as features do aluno a partir das respostas e dos simulados da
turma, chama o `ml_service` (scikit-learn) e persiste/atualiza a previsão mais recente.
As queries ficam no `predicao_repository`; o modelo, no `ml_service`.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
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
    ids_avaliaveis = {s.id for s in avaliaveis}

    # Só as respostas dentro do universo avaliável desta turma — assim as três features
    # (participação, acerto e média) saem do mesmo conjunto e ficam coerentes mesmo se
    # houver respostas de outra turma (ex.: aluno transferido).
    respostas = [
        r
        for r in predicao_repository.respostas_do_aluno(sessao, aluno.id)
        if r.simulado_id in ids_avaliaveis
    ]
    respondidas = len(respostas)
    acertos = sum(1 for r in respostas if r.correta)
    taxa_acerto = acertos / respondidas if respondidas else 0.0

    # Participação: simulados em que respondeu ao menos 1 questão / avaliáveis.
    # (Aproximação consciente do MVP: respondeu 1 questão conta como participação no simulado.)
    ids_respondidos = {r.simulado_id for r in respostas}
    taxa_participacao = len(ids_respondidos) / len(ids_avaliaveis)

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


def _aplicar(predicao: PredicaoRisco, resultado: dict, modelo_versao: str) -> None:
    predicao.score_risco = resultado["score_risco"]
    predicao.classificacao = resultado["classificacao"]
    predicao.fatores = resultado["fatores"]
    predicao.modelo_versao = modelo_versao
    # Explícito (não confia no onupdate): faz o timestamp avançar mesmo quando o
    # resultado é idêntico ao anterior — aí o SQLAlchemy não emitiria UPDATE sozinho.
    predicao.calculada_em = func.now()


def calcular_risco(sessao: Session, *, aluno_id: int) -> PredicaoRisco:
    aluno = sessao.get(Aluno, aluno_id)
    if aluno is None:
        raise NaoEncontrado(f"aluno {aluno_id} não encontrado")

    features = _features(sessao, aluno)
    if features is None:
        # Sem dados para prever: 'indeterminado' é o discriminador. score_risco=0.0 é
        # só placeholder — não ordenar por ele quando classificacao == 'indeterminado'.
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
    _aplicar(predicao, resultado, modelo_versao)

    try:
        sessao.commit()
    except IntegrityError:
        # Corrida na 1ª gravação do mesmo aluno (índice unique em aluno_id): recupera a
        # linha que a outra requisição inseriu e atualiza, em vez de estourar 500.
        sessao.rollback()
        predicao = sessao.scalar(
            select(PredicaoRisco).where(PredicaoRisco.aluno_id == aluno_id)
        )
        _aplicar(predicao, resultado, modelo_versao)
        sessao.commit()

    sessao.refresh(predicao)
    return predicao
