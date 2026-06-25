"""Cliente fino para a Claude API (Anthropic).

Esta camada NÃO tem regra de negócio: ela só sabe falar com a API e devolver
JSON validado contra um schema (ou sinalizar que a IA está indisponível). A regra
de curadoria — montar o prompt, validar a seleção, decidir o fallback — vive em
`app/services/ia_curadoria_service.py`.

Resiliência por desenho:
- o pacote `anthropic` é importado preguiçosamente (dentro das funções), então o
  backend roda normalmente mesmo sem a dependência instalada — só com a IA desligada;
- qualquer falha (timeout, erro de API, recusa, JSON inválido) vira `IAIndisponivel`,
  e o chamador cai na seleção clássica do prova_service.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class IAIndisponivel(Exception):
    """A curadoria por IA não pôde ser concluída; use o fallback clássico."""


def disponivel() -> bool:
    """True só quando a IA está habilitada, há chave e o pacote `anthropic` existe."""
    if not settings.ia_curadoria_habilitada or not settings.anthropic_api_key:
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        logger.warning(
            "SEDU_IA_CURADORIA_HABILITADA=true, mas o pacote 'anthropic' não está "
            "instalado. Rode 'pip install -r requirements.txt'. Usando fallback clássico."
        )
        return False
    return True


@lru_cache(maxsize=1)
def _cliente():
    # Memoizado: lê a config no 1º uso. Trocar SEDU_ANTHROPIC_API_KEY/timeout/retries
    # exige reiniciar o processo (config é imutável por ambiente).
    import anthropic

    return anthropic.Anthropic(
        api_key=settings.anthropic_api_key,
        timeout=settings.claude_timeout_segundos,
        max_retries=settings.claude_max_retries,
    )


def completar_json(
    *, system: str, conteudo: str, schema: dict[str, Any], max_tokens: int = 16000
) -> dict[str, Any]:
    """Pede à Claude API uma resposta JSON validada contra `schema`.

    - prompt caching no bloco `system` (a parte estável do prompt);
    - thinking adaptativo (recomendado para a tarefa de raciocínio pedagógico);
    - structured outputs (`output_config.format`) para garantir JSON parseável.

    Levanta `IAIndisponivel` em qualquer falha — o serviço chamador cai no fallback.
    """
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - guarda redundante de disponivel()
        raise IAIndisponivel("pacote 'anthropic' indisponível") from exc

    try:
        resposta = _cliente().messages.create(
            model=settings.claude_modelo,
            max_tokens=max_tokens,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": conteudo}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
    except anthropic.APIError as exc:
        # Detalhe (e tipo) só no log do servidor; a mensagem que sobe é genérica
        # para não persistir/expor o corpo de erro da Anthropic em parametros_json.
        logger.warning("Falha na Claude API (%s): %s", type(exc).__name__, exc)
        raise IAIndisponivel("falha na chamada à Claude API") from exc
    except Exception as exc:  # rede, parâmetro do SDK não suportado (ex.: versão antiga), etc.
        logger.warning("Erro inesperado na Claude API (%s): %s", type(exc).__name__, exc)
        raise IAIndisponivel("erro inesperado na Claude API") from exc

    if resposta.stop_reason == "refusal":
        raise IAIndisponivel("a Claude API recusou a requisição (stop_reason=refusal)")
    if resposta.stop_reason == "max_tokens":
        raise IAIndisponivel("resposta da Claude API truncada (max_tokens atingido)")

    texto = next(
        (b.text for b in resposta.content if getattr(b, "type", None) == "text"), None
    )
    if not texto:
        raise IAIndisponivel("resposta da Claude API sem conteúdo de texto")
    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        raise IAIndisponivel("resposta da Claude API não é JSON válido") from exc
