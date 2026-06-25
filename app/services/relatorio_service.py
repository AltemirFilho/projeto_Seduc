from __future__ import annotations

import csv
import io
from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from app.exceptions import NaoEncontrado
from app.repositories import resposta_repository, turma_repository

# Caracteres que disparam fórmula no Excel/Sheets quando abrem a 1ª posição.
_CSV_PERIGO = ("=", "+", "-", "@", "\t", "\r")


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


def _sanitizar_csv(valor) -> str:
    texto = "" if valor is None else str(valor)
    if texto[:1] in _CSV_PERIGO:
        return "'" + texto  # neutraliza injeção de fórmula
    return texto


def _pct(fracao: float) -> str:
    return f"{round(fracao * 100, 1)}%"


def exportar_csv(relatorio: dict) -> str:
    """Serializa o relatório em CSV (delimitador ';' e BOM, p/ Excel pt-BR)."""
    buf = io.StringIO()
    escritor = csv.writer(buf, delimiter=";", lineterminator="\n")
    turma = relatorio["turma"]
    resumo = [
        ("Turma", turma["nome"]),
        ("Série", turma["serie"]),
        ("Ano letivo", turma["ano_letivo"]),
        ("Total de alunos", relatorio["total_alunos"]),
        ("Total de respostas", relatorio["total_respostas"]),
        ("Total de acertos", relatorio["total_acertos"]),
        ("Média de acerto", _pct(relatorio["media_acerto"])),
    ]
    for chave, valor in resumo:
        escritor.writerow([_sanitizar_csv(chave), _sanitizar_csv(valor)])

    escritor.writerow([])
    escritor.writerow(
        ["Conteúdo", "Matéria", "Respostas", "Acertos", "Erros", "Taxa de erro"]
    )
    for c in relatorio["conteudos"]:
        escritor.writerow(
            [
                _sanitizar_csv(c["conteudo"]),
                _sanitizar_csv(c["materia"]),
                c["total"],
                c["acertos"],
                c["erros"],
                _pct(c["taxa_erro"]),
            ]
        )
    return chr(0xFEFF) + buf.getvalue()  # BOM (U+FEFF): acentos corretos no Excel


def exportar_pdf(relatorio: dict) -> bytes:
    """Renderiza o relatório como PDF (reportlab importado sob demanda)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    turma = relatorio["turma"]
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, title=f"Relatório da turma {turma['nome']}"
    )
    estilos = getSampleStyleSheet()
    elementos = [
        Paragraph(
            f"Relatório de desempenho — Turma {escape(str(turma['nome']))}",
            estilos["Title"],
        ),
        Paragraph(
            f"{escape(str(turma['serie']))} · Ano letivo {turma['ano_letivo']}",
            estilos["Normal"],
        ),
        Spacer(1, 12),
        Paragraph(
            f"Alunos: {relatorio['total_alunos']} | "
            f"Respostas: {relatorio['total_respostas']} | "
            f"Acertos: {relatorio['total_acertos']} | "
            f"Média de acerto: {_pct(relatorio['media_acerto'])}",
            estilos["Normal"],
        ),
        Spacer(1, 16),
        Paragraph("Conteúdos por taxa de erro", estilos["Heading2"]),
    ]

    linhas = [["Conteúdo", "Matéria", "Respostas", "Acertos", "Erros", "Taxa de erro"]]
    for c in relatorio["conteudos"]:
        linhas.append(
            [
                c["conteudo"],
                c["materia"],
                c["total"],
                c["acertos"],
                c["erros"],
                _pct(c["taxa_erro"]),
            ]
        )
    tabela = Table(linhas, hAlign="LEFT")
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f2f2f2")],
                ),
            ]
        )
    )
    elementos.append(tabela)
    doc.build(elementos)
    return buf.getvalue()
