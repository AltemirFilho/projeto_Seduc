"""Curadoria de simulado por IA (Claude API).

Pede à Claude API uma seleção ORDENADA de questões a partir das candidatas do banco,
respeitando quantidade, distribuição de dificuldade e variedade de conteúdo. A resposta
da IA é sempre revalidada contra as candidatas reais (anti-alucinação): IDs inexistentes,
duplicados, quantidade errada ou confiança baixa derrubam para o fallback clássico.

O serviço só decide *quais* questões entram e em que ordem; a montagem da prova
(embaralhar alternativas, achar gabarito) continua sendo do `prova_service`, que recebe
os IDs via parâmetro `selecao_ids`.
"""

from __future__ import annotations

import logging
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.config import settings
from app.integrations import claude
from app.models import Questao
from app.repositories import questao_repository

logger = logging.getLogger(__name__)

_SCHEMA_SELECAO = {
    "type": "object",
    "properties": {
        "questao_ids": {"type": "array", "items": {"type": "integer"}},
        "confianca": {"type": "number"},
    },
    "required": ["questao_ids", "confianca"],
    "additionalProperties": False,
}

_SYSTEM = """Você é um curador pedagógico de simulados da rede pública de Sergipe (SEDUC-SE).
Recebe uma lista de questões candidatas (cada uma com id, matéria, conteúdo e nível de
dificuldade) e os parâmetros do simulado. Sua tarefa é SELECIONAR e ORDENAR as questões que
formam o melhor simulado, respeitando:
- a quantidade pedida;
- a distribuição de dificuldade desejada, quando informada;
- variedade de conteúdos (evitar concentrar tudo no mesmo tópico);
- uma curva de dificuldade progressiva (questões mais fáceis no começo), quando fizer sentido.

Regras inegociáveis:
- Escolha APENAS ids presentes na lista de candidatas.
- Não invente questões nem repita ids.
- Devolva exatamente a quantidade pedida.
- 'confianca' é um número de 0 a 1 indicando o quanto a seleção atende bem aos critérios."""


def _descrever_candidatas(candidatas: list[Questao]) -> str:
    linhas = []
    for q in candidatas:
        enunciado = " ".join((q.enunciado or "").split())
        if len(enunciado) > 160:
            enunciado = enunciado[:157] + "..."
        linhas.append(
            f"id={q.id} | materia={q.materia.nome} | conteudo={q.conteudo.nome} "
            f"| nivel={q.nivel.nome} | enunciado: {enunciado}"
        )
    return "\n".join(linhas)


def _distribuicao_respeitada(
    ids: list[int],
    candidatas: list[Questao],
    distribuicao: Optional[dict[str, float]],
    quantidade: int,
) -> bool:
    """A seleção da IA respeita a distribuição de dificuldade pedida (com tolerância)?

    Sem distribuição pedida, nada a checar. A folga (em nº de questões) por nível evita
    rejeitar a seleção só por arredondamento — espelha o melhor-esforço do caminho
    clássico em vez de exigir uma curva exata.
    """
    if not distribuicao:
        return True
    nivel_por_id = {q.id: q.nivel.nome for q in candidatas}
    contagem: dict[str, int] = {}
    for i in ids:
        nome = nivel_por_id.get(i)
        contagem[nome] = contagem.get(nome, 0) + 1
    folga = max(1, round(settings.ia_curadoria_tolerancia_distribuicao * quantidade))
    for nivel_nome, proporcao in distribuicao.items():
        alvo = round(quantidade * proporcao)
        if abs(contagem.get(nivel_nome, 0) - alvo) > folga:
            return False
    return True


def selecionar_questoes(
    sessao: Session,
    *,
    serie: str,
    materia: Optional[str] = None,
    materias: Optional[Sequence[str]] = None,
    conteudos: Optional[Sequence[str]] = None,
    distribuicao: Optional[dict[str, float]] = None,
    quantidade: int = 10,
    adaptacoes: Optional[Sequence[str]] = None,
) -> tuple[Optional[list[int]], dict]:
    """Pede à IA uma seleção ordenada de IDs de questões.

    Retorna `(ids, meta)`:
    - `ids` é uma lista de IDs na ordem sugerida pela IA, ou `None` para sinalizar ao
      chamador que use o fallback clássico do prova_service;
    - `meta` sempre traz `{'fonte', 'motivo', 'confianca'}` para registro/observabilidade.
    """
    if not claude.disponivel():
        return None, {"fonte": "classico", "motivo": "ia_desabilitada", "confianca": None}

    materias_filtro = list(materias) if materias else ([materia] if materia else [])
    candidatas = questao_repository.filtrar_questoes(
        sessao,
        serie=serie,
        materias=materias_filtro or None,
        conteudos=conteudos,
        adaptacoes=adaptacoes,
    )
    if len(candidatas) <= quantidade:
        # Sem excedente não há o que curar: a seleção seria trivialmente todas as candidatas.
        return None, {
            "fonte": "classico",
            "motivo": "candidatas_insuficientes",
            "confianca": None,
        }

    teto = settings.ia_curadoria_max_candidatas
    candidatas_ia = candidatas[:teto] if len(candidatas) > teto else candidatas
    ids_validos = {q.id for q in candidatas_ia}

    conteudo = (
        "Parâmetros do simulado:\n"
        f"- série: {serie}\n"
        f"- matérias: {materias_filtro or 'todas'}\n"
        f"- quantidade: {quantidade}\n"
        f"- distribuição de dificuldade desejada: {distribuicao or 'não especificada'}\n\n"
        f"Questões candidatas ({len(candidatas_ia)}):\n"
        f"{_descrever_candidatas(candidatas_ia)}"
    )

    try:
        resultado = claude.completar_json(
            system=_SYSTEM, conteudo=conteudo, schema=_SCHEMA_SELECAO
        )
    except claude.IAIndisponivel as exc:
        logger.warning("Curadoria por IA falhou, usando fallback clássico: %s", exc)
        return None, {"fonte": "classico", "motivo": "ia_falhou", "confianca": None}

    confianca = resultado.get("confianca")

    # Validação adversarial: só confiamos em IDs reais, únicos e na quantidade certa.
    ids_limpos: list[int] = []
    vistos: set[int] = set()
    for i in resultado.get("questao_ids") or []:
        if isinstance(i, int) and i in ids_validos and i not in vistos:
            ids_limpos.append(i)
            vistos.add(i)

    if len(ids_limpos) < quantidade:
        logger.warning(
            "Seleção da IA inválida (esperava %d IDs válidos e únicos, vieram %d); "
            "fallback clássico.",
            quantidade,
            len(ids_limpos),
        )
        return None, {
            "fonte": "classico",
            "motivo": "selecao_ia_invalida",
            "confianca": confianca,
        }

    # Falha fechado: confiança ausente/não-numérica (ou booleana) não é confiável.
    # bool é subclasse de int em Python, então excluímos explicitamente.
    if not isinstance(confianca, (int, float)) or isinstance(confianca, bool):
        logger.warning("Confiança da IA inválida (%r); fallback clássico.", confianca)
        return None, {
            "fonte": "classico",
            "motivo": "confianca_invalida",
            "confianca": confianca,
        }

    if confianca < settings.ia_curadoria_confianca_minima:
        logger.info(
            "Confiança da IA (%.2f) abaixo do mínimo (%.2f); fallback clássico.",
            confianca,
            settings.ia_curadoria_confianca_minima,
        )
        return None, {
            "fonte": "classico",
            "motivo": "baixa_confianca",
            "confianca": confianca,
        }

    selecionados = ids_limpos[:quantidade]
    # A distribuição entra no prompt como desejo; aqui garantimos que a seleção da IA
    # de fato a respeita (com tolerância), senão caímos no clássico — que a impõe.
    if not _distribuicao_respeitada(selecionados, candidatas_ia, distribuicao, quantidade):
        logger.info("Seleção da IA não respeitou a distribuição pedida; fallback clássico.")
        return None, {
            "fonte": "classico",
            "motivo": "distribuicao_nao_atendida",
            "confianca": confianca,
        }

    return selecionados, {"fonte": "ia", "motivo": None, "confianca": confianca}
