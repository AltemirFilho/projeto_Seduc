from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions import NaoEncontrado
from app.repositories import resposta_repository, turma_repository


def _taxa(parte: int, total: int) -> float:
    return round(parte / total, 4) if total else 0.0


def relatorio_turma(sessao: Session, turma_id: int) -> dict:
    """Desempenho da turma derivado das respostas (sem IA): média de acerto e
    ranking de conteúdos por taxa de erro."""
    turma = turma_repository.buscar_por_id(sessao, turma_id)
    if turma is None:
        raise NaoEncontrado(f"Turma {turma_id} não encontrada")

    total_respostas, total_acertos = resposta_repository.estatisticas_turma(
        sessao, turma_id
    )

    conteudos = [
        {
            "conteudo": conteudo,
            "materia": materia,
            "total": total,
            "acertos": acertos,
            "erros": total - acertos,
            "taxa_erro": _taxa(total - acertos, total),
        }
        for conteudo, materia, total, acertos in resposta_repository.desempenho_por_conteudo(
            sessao, turma_id
        )
    ]
    # Mais errados primeiro; desempata por volume e nome para uma ordem estável.
    conteudos.sort(key=lambda c: (-c["taxa_erro"], -c["erros"], c["conteudo"]))

    return {
        "turma": {
            "id": turma.id,
            "nome": turma.nome,
            "serie": turma.serie.nome,
            "ano_letivo": turma.ano_letivo,
        },
        "total_alunos": resposta_repository.contar_alunos_turma(sessao, turma_id),
        "total_respostas": total_respostas,
        "total_acertos": total_acertos,
        "media_acerto": _taxa(total_acertos, total_respostas),
        "conteudos": conteudos,
    }
