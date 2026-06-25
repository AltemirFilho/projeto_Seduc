"""Modelo de predição de risco de evasão (scikit-learn).

Camada de integração: NÃO tem regra de negócio nem acesso a banco. Recebe as features
já calculadas (média de nota, taxa de participação, taxa de acerto) e devolve um score
de risco + classificação + os fatores que explicam o resultado.

Como não há histórico rotulado de evasão num MVP, o LogisticRegression é treinado num
conjunto-semente que codifica a regra de domínio (engajamento/desempenho baixos => risco):
o modelo aprende pesos sensatos e os aplica aos alunos reais. Precisão de verdade exige
rótulos reais depois — fica registrado como trabalho futuro. O `anthropic`-style: o
scikit-learn é importado preguiçosamente, então o app sobe mesmo sem o pacote (o endpoint
de risco é que vai falhar claro se faltar).
"""

from __future__ import annotations

from functools import lru_cache

MODELO_VERSAO = "logreg-v1"

# Conjunto-semente. Features escaladas em 0..1: (media/10, participacao, acerto).
# y = 1 (em risco) quando engajamento/desempenho são baixos; 0 caso contrário.
_SEMENTE: list[tuple[tuple[float, float, float], int]] = [
    ((0.90, 1.00, 0.90), 0),
    ((0.85, 0.95, 0.85), 0),
    ((0.80, 0.90, 0.80), 0),
    ((0.75, 1.00, 0.75), 0),
    ((0.70, 0.85, 0.70), 0),
    ((0.65, 0.90, 0.65), 0),
    ((0.70, 0.80, 0.60), 0),
    ((0.60, 0.75, 0.65), 0),
    ((0.35, 0.40, 0.40), 1),
    ((0.30, 0.30, 0.35), 1),
    ((0.20, 0.20, 0.30), 1),
    ((0.10, 0.15, 0.20), 1),
    ((0.45, 0.30, 0.45), 1),
    ((0.50, 0.25, 0.50), 1),  # desempenho ok, mas participação baixa => risco
    ((0.40, 0.35, 0.40), 1),
    ((0.25, 0.45, 0.30), 1),
]

# Limiares de classificação a partir do score (probabilidade de risco).
_LIMITE_BAIXO = 0.34
_LIMITE_MEDIO = 0.67


@lru_cache(maxsize=1)
def _modelo():
    from sklearn.linear_model import LogisticRegression

    X = [list(features) for features, _ in _SEMENTE]
    y = [rotulo for _, rotulo in _SEMENTE]
    modelo = LogisticRegression(max_iter=1000)
    modelo.fit(X, y)
    return modelo


def _classificar(score: float) -> str:
    if score < _LIMITE_BAIXO:
        return "baixo"
    if score < _LIMITE_MEDIO:
        return "medio"
    return "alto"


def _fatores(
    media_nota: float,
    taxa_participacao: float,
    taxa_acerto: float,
    classificacao: str,
) -> list[str]:
    """Explicação coerente com a classificação (a previsão nunca é caixa-preta).

    Risco baixo => sem fatores. Risco médio/alto => sempre ao menos um fator: os
    sinais abaixo do ideal, ou um motivo genérico honesto quando nenhum sinal isolado
    se destaca (o conjunto é que puxou o risco). Os limiares são mais generosos que a
    fronteira do modelo de propósito, para nunca contradizer a classificação.
    """
    if classificacao == "baixo":
        return ["sem fatores de risco relevantes"]
    fatores: list[str] = []
    if taxa_participacao < 0.6:
        fatores.append(f"participação baixa ({taxa_participacao * 100:.0f}%)")
    if media_nota < 6.0:
        fatores.append(f"média baixa ({media_nota:.1f})")
    if taxa_acerto < 0.6:
        fatores.append(f"taxa de acerto baixa ({taxa_acerto * 100:.0f}%)")
    return fatores or ["desempenho e engajamento intermediários"]


def prever(
    *, media_nota: float, taxa_participacao: float, taxa_acerto: float
) -> dict:
    """Devolve {score_risco, classificacao, fatores} para as features de um aluno."""
    features = [[media_nota / 10.0, taxa_participacao, taxa_acerto]]
    # Arredonda uma vez só e classifica a partir DESSE valor, para o rótulo bater
    # sempre com o número devolvido/persistido (sem divergência na borda do limiar).
    score = round(float(_modelo().predict_proba(features)[0][1]), 4)
    classificacao = _classificar(score)
    return {
        "score_risco": score,
        "classificacao": classificacao,
        "fatores": _fatores(media_nota, taxa_participacao, taxa_acerto, classificacao),
    }
