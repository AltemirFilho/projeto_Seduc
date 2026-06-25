"""Relatórios derivados das respostas/resultados (sem IA).

- relatório da turma: média, nº de alunos e ranking de conteúdos por taxa de erro;
- "meu-resultado": a visão individual do aluno (nota + acertou/errou + gabarito);
- exportação em CSV e PDF.

Tudo deriva da tabela `respostas` + dos resultados persistidos em `resultados_simulado`.
"""

from __future__ import annotations

import csv
import io

from sqlalchemy.orm import Session

from app.enums import StatusSimulado
from app.exceptions import NaoEncontrado, PermissaoNegada, RegraNegocio
from app.models import Aluno, Simulado
from app.repositories import resposta_repository, turma_repository

LETRAS = "ABCDE"


def relatorio_turma(sessao: Session, *, turma_id: int) -> dict:
    turma = turma_repository.buscar_por_id(sessao, turma_id)
    if turma is None:
        raise NaoEncontrado(f"turma {turma_id} não encontrada")

    n_alunos = resposta_repository.contar_alunos_da_turma(sessao, turma_id)
    resultados = resposta_repository.resultados_da_turma(sessao, turma_id)
    media = (
        round(sum(r.nota for r in resultados) / len(resultados), 2)
        if resultados
        else 0.0
    )

    por_conteudo: dict[str, list[int]] = {}  # nome -> [total, erros]
    for r in resposta_repository.respostas_da_turma(sessao, turma_id):
        nome = r.questao.conteudo.nome
        reg = por_conteudo.setdefault(nome, [0, 0])
        reg[0] += 1
        if not r.correta:
            reg[1] += 1

    conteudos = sorted(
        (
            {
                "conteudo": nome,
                "total": total,
                "erros": erros,
                "taxa_erro": round(erros / total, 2) if total else 0.0,
            }
            for nome, (total, erros) in por_conteudo.items()
        ),
        key=lambda c: c["taxa_erro"],
        reverse=True,
    )

    return {
        "turma_id": turma_id,
        "turma": turma.nome,
        "alunos": n_alunos,
        "simulados_corrigidos": len({r.simulado_id for r in resultados}),
        "media_turma": media,
        "conteudos": conteudos,
    }


def meu_resultado(sessao: Session, *, simulado_id: int, aluno: Aluno) -> dict:
    """Resultado individual do aluno num simulado finalizado da própria turma."""
    simulado = sessao.get(Simulado, simulado_id)
    if simulado is None:
        raise NaoEncontrado(f"simulado {simulado_id} não encontrado")
    if aluno.turma_id != simulado.turma_id:
        raise PermissaoNegada(
            "este simulado não pertence à sua turma", codigo="fora_da_turma"
        )
    if simulado.status != StatusSimulado.FINALIZADO:
        raise RegraNegocio(
            "o resultado fica disponível depois que o simulado é finalizado",
            codigo="simulado_nao_finalizado",
        )

    resultado = resposta_repository.resultado_do_aluno(
        sessao, aluno_id=aluno.id, simulado_id=simulado_id
    )
    minhas = {
        r.questao_id: r
        for r in resposta_repository.respostas_do_aluno_no_simulado(
            sessao, aluno_id=aluno.id, simulado_id=simulado_id
        )
    }

    questoes: list[dict] = []
    for sq in sorted(simulado.questoes, key=lambda x: x.ordem_questao):
        questao = sq.questao
        alt_por_id = {a.id: a for a in questao.alternativas}
        gabarito = None
        sua_letra = None
        minha = minhas.get(questao.id)
        for letra, alt_id in zip(LETRAS, sq.alternativas_ordem):
            alt = alt_por_id.get(alt_id)
            if alt is None:
                continue
            if alt.correta:
                gabarito = letra
            if minha is not None and alt_id == minha.alternativa_id:
                sua_letra = letra
        questoes.append(
            {
                "ordem": sq.ordem_questao,
                "questao_id": questao.id,
                "enunciado": questao.enunciado,
                "conteudo": questao.conteudo.nome,
                "sua_resposta": sua_letra,
                "gabarito": gabarito,
                "acertou": bool(minha.correta) if minha is not None else None,
            }
        )

    return {
        "simulado_id": simulado_id,
        "aluno_id": aluno.id,
        "nota": resultado.nota if resultado else 0.0,
        "acertos": resultado.acertos if resultado else 0,
        "total_questoes": (
            resultado.total_questoes if resultado else len(simulado.questoes)
        ),
        "questoes": questoes,
    }


def exportar_turma_csv(sessao: Session, *, turma_id: int) -> str:
    rel = relatorio_turma(sessao, turma_id=turma_id)
    buf = io.StringIO()
    escritor = csv.writer(buf)
    escritor.writerow(["Turma", rel["turma"] or turma_id])
    escritor.writerow(["Alunos", rel["alunos"]])
    escritor.writerow(["Simulados corrigidos", rel["simulados_corrigidos"]])
    escritor.writerow(["Média da turma", rel["media_turma"]])
    escritor.writerow([])
    escritor.writerow(["Conteúdo", "Total de respostas", "Erros", "Taxa de erro"])
    for c in rel["conteudos"]:
        escritor.writerow(
            [c["conteudo"], c["total"], c["erros"], f"{c['taxa_erro'] * 100:.0f}%"]
        )
    return buf.getvalue()


def exportar_turma_pdf(sessao: Session, *, turma_id: int) -> bytes:
    rel = relatorio_turma(sessao, turma_id=turma_id)
    # Import preguiçoso do reportlab (mantém a app rodável sem o pacote, como o resto do
    # projeto faz com anthropic/sklearn).
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:  # pragma: no cover
        raise RegraNegocio(
            "exportação em PDF indisponível (reportlab não instalado)",
            codigo="pdf_indisponivel",
        ) from exc

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Relatório turma {turma_id}")
    estilos = getSampleStyleSheet()
    elementos = [
        Paragraph(f"Relatório da turma {rel['turma'] or turma_id}", estilos["Title"]),
        Paragraph(
            f"Alunos: {rel['alunos']} &nbsp;&nbsp; "
            f"Média da turma: {rel['media_turma']:.2f} &nbsp;&nbsp; "
            f"Simulados corrigidos: {rel['simulados_corrigidos']}",
            estilos["Normal"],
        ),
        Spacer(1, 0.5 * cm),
    ]
    dados = [["Conteúdo", "Total", "Erros", "Taxa de erro"]]
    for c in rel["conteudos"]:
        dados.append(
            [c["conteudo"], str(c["total"]), str(c["erros"]), f"{c['taxa_erro'] * 100:.0f}%"]
        )
    tabela = Table(dados, hAlign="LEFT")
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2A2018")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6EFE1")]),
            ]
        )
    )
    elementos.append(tabela)
    doc.build(elementos)
    return buf.getvalue()
