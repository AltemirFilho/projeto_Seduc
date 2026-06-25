"""Diagnóstico pedagógico por IA (Frente B / IA).

Para um simulado FINALIZADO, agrega os resultados da turma (média, taxa de erro por
conteúdo) e pede à Claude um diagnóstico: resumo + pontos fracos + recomendações.
Resiliente: se a IA estiver indisponível (sem chave/timeout/erro), degrada para os
dados crus (modelo_versao='indisponivel'), sempre devolvendo algo útil ao gestor.

Reusa o app/integrations/claude.py da curadoria; o liga/desliga é o mesmo flag de IA
(SEDU_IA_CURADORIA_HABILITADA) que claude.disponivel() já consulta.
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.enums import StatusSimulado
from app.exceptions import NaoEncontrado, RegraNegocio
from app.integrations import claude
from app.models import DiagnosticoTurma, Simulado
from app.repositories import diagnostico_repository

logger = logging.getLogger(__name__)

_SCHEMA = {
    "type": "object",
    "properties": {
        "resumo": {"type": "string"},
        "pontos_fracos": {"type": "array", "items": {"type": "string"}},
        "recomendacoes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["resumo", "pontos_fracos", "recomendacoes"],
    "additionalProperties": False,
}

_SYSTEM = """Você é um analista pedagógico da Secretaria de Educação de Sergipe (SEDUC-SE).
Recebe os resultados agregados de um simulado JÁ FINALIZADO de uma turma (média da turma,
número de alunos avaliados e a taxa de erro por conteúdo) e produz um diagnóstico para o
gestor/professor, com:
- resumo: um parágrafo claro sobre o desempenho da turma, destacando forças e fragilidades;
- pontos_fracos: os conteúdos/habilidades em que a turma mais errou (use os nomes informados);
- recomendacoes: ações pedagógicas concretas e priorizadas para a turma evoluir nesses pontos.

Seja específico, prático e baseie-se APENAS nos dados informados. Escreva em português."""

# Acima desta taxa de erro, o conteúdo entra como ponto fraco no fallback sem IA.
_LIMITE_PONTO_FRACO = 0.5


def _agregados(simulado: Simulado, respostas: list) -> dict:
    total_questoes = len(simulado.questoes)
    por_conteudo: dict[str, list[int]] = {}  # nome -> [total, erros]
    acertos_por_aluno: dict[int, int] = {}
    for r in respostas:
        nome = r.questao.conteudo.nome
        registro = por_conteudo.setdefault(nome, [0, 0])
        registro[0] += 1
        if not r.correta:
            registro[1] += 1
        acertos_por_aluno.setdefault(r.aluno_id, 0)
        if r.correta:
            acertos_por_aluno[r.aluno_id] += 1

    notas = [
        10 * acertos / total_questoes for acertos in acertos_por_aluno.values()
    ] if total_questoes else []
    media_turma = round(sum(notas) / len(notas), 2) if notas else 0.0

    conteudos = sorted(
        (
            {
                "conteudo": nome,
                "total": total,
                "erros": erros,
                "taxa_erro": round(erros / total, 2),
            }
            for nome, (total, erros) in por_conteudo.items()
            if total
        ),
        key=lambda c: c["taxa_erro"],
        reverse=True,
    )
    return {
        "media_turma": media_turma,
        "alunos_avaliados": len(acertos_por_aluno),
        "total_questoes": total_questoes,
        "conteudos": conteudos,
    }


def _descrever(agregados: dict) -> str:
    linhas = [
        f"Média da turma: {agregados['media_turma']:.2f} (0 a 10)",
        f"Alunos avaliados: {agregados['alunos_avaliados']}",
        f"Total de questões: {agregados['total_questoes']}",
        "Taxa de erro por conteúdo (maior primeiro):",
    ]
    for c in agregados["conteudos"]:
        linhas.append(
            f"- {c['conteudo']}: {c['taxa_erro'] * 100:.0f}% de erro "
            f"({c['erros']}/{c['total']} respostas)"
        )
    return "\n".join(linhas)


def _fallback(agregados: dict) -> dict:
    """Diagnóstico sem IA: usa os agregados crus como pontos fracos."""
    fracos = [
        c["conteudo"]
        for c in agregados["conteudos"]
        if c["taxa_erro"] >= _LIMITE_PONTO_FRACO
    ]
    if not fracos:  # nenhum acima do limite: pega os 3 com maior erro
        fracos = [c["conteudo"] for c in agregados["conteudos"][:3]]
    return {
        "resumo": (
            f"Diagnóstico automático por IA indisponível. Média da turma "
            f"{agregados['media_turma']:.2f} com {agregados['alunos_avaliados']} "
            f"aluno(s) avaliado(s). Veja os conteúdos com maior taxa de erro."
        ),
        "pontos_fracos": fracos,
        "recomendacoes": [],
    }


def _aplicar(diagnostico: DiagnosticoTurma, resultado: dict, modelo_versao: str) -> None:
    diagnostico.resumo = resultado["resumo"]
    diagnostico.pontos_fracos = resultado["pontos_fracos"]
    diagnostico.recomendacoes = resultado["recomendacoes"]
    diagnostico.modelo_versao = modelo_versao
    # Explícito: faz o timestamp avançar mesmo num resultado idêntico (o onupdate não
    # dispara quando nada muda) — mesma lição da predição de risco.
    diagnostico.gerado_em = func.now()


def gerar_diagnostico(sessao: Session, *, simulado_id: int) -> DiagnosticoTurma:
    simulado = sessao.get(Simulado, simulado_id)
    if simulado is None:
        raise NaoEncontrado(f"simulado {simulado_id} não encontrado")
    if simulado.status != StatusSimulado.FINALIZADO:
        raise RegraNegocio(
            "só simulados finalizados podem ser diagnosticados",
            codigo="simulado_nao_finalizado",
        )

    respostas = diagnostico_repository.respostas_do_simulado(sessao, simulado_id)
    agregados = _agregados(simulado, respostas)

    if not respostas:
        resultado = {
            "resumo": "Nenhuma resposta registrada neste simulado; não há o que diagnosticar.",
            "pontos_fracos": [],
            "recomendacoes": [],
        }
        modelo_versao = "indisponivel"
    elif claude.disponivel():
        try:
            ia = claude.completar_json(
                system=_SYSTEM, conteudo=_descrever(agregados), schema=_SCHEMA
            )
            resumo = (ia.get("resumo") or "").strip()
            if not resumo:
                raise claude.IAIndisponivel("resumo vazio")
            resultado = {
                "resumo": resumo,
                "pontos_fracos": ia.get("pontos_fracos") or [],
                "recomendacoes": ia.get("recomendacoes") or [],
            }
            modelo_versao = settings.claude_modelo
        except claude.IAIndisponivel as exc:
            logger.warning("Diagnóstico por IA falhou, degradando aos dados crus: %s", exc)
            resultado = _fallback(agregados)
            modelo_versao = "indisponivel"
    else:
        resultado = _fallback(agregados)
        modelo_versao = "indisponivel"

    diagnostico = sessao.scalar(
        select(DiagnosticoTurma).where(DiagnosticoTurma.simulado_id == simulado_id)
    )
    if diagnostico is None:
        diagnostico = DiagnosticoTurma(simulado_id=simulado_id)
        sessao.add(diagnostico)
    _aplicar(diagnostico, resultado, modelo_versao)

    try:
        sessao.commit()
    except IntegrityError:
        # Corrida na 1ª gravação do mesmo simulado (índice unique): recupera e atualiza.
        sessao.rollback()
        diagnostico = sessao.scalar(
            select(DiagnosticoTurma).where(DiagnosticoTurma.simulado_id == simulado_id)
        )
        _aplicar(diagnostico, resultado, modelo_versao)
        sessao.commit()

    sessao.refresh(diagnostico)
    return diagnostico
