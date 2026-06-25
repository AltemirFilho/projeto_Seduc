from app.services import relatorio_service

_FAKE = {
    "turma": {"id": 1, "nome": "9A", "serie": "9º ano", "ano_letivo": 2026},
    "total_alunos": 2,
    "total_respostas": 8,
    "total_acertos": 4,
    "media_acerto": 0.5,
    "conteudos": [
        {
            "conteudo": "Geometria",
            "materia": "Matemática",
            "total": 4,
            "acertos": 1,
            "erros": 3,
            "taxa_erro": 0.75,
        },
        {
            "conteudo": "=cmd()|calc",  # tentativa de injeção de fórmula
            "materia": "Matemática",
            "total": 4,
            "acertos": 3,
            "erros": 1,
            "taxa_erro": 0.25,
        },
    ],
}


def test_exportar_csv_estrutura_e_bom():
    texto = relatorio_service.exportar_csv(_FAKE)
    assert texto.startswith("﻿")  # BOM p/ Excel
    assert "9A" in texto and "Geometria" in texto
    assert "75.0%" in texto  # taxa de erro formatada


def test_exportar_csv_neutraliza_injecao():
    texto = relatorio_service.exportar_csv(_FAKE)
    # a célula perigosa vira "'=cmd()..." e não sobra "=cmd()" solto
    assert "'=cmd()|calc" in texto
    assert "=cmd()|calc" not in texto.replace("'=cmd()|calc", "")


def test_exportar_pdf_magic_bytes():
    pdf = relatorio_service.exportar_pdf(_FAKE)
    assert isinstance(pdf, (bytes, bytearray))
    assert bytes(pdf[:5]) == b"%PDF-"
    assert len(pdf) > 500


def test_endpoint_csv(client, h_gestor, dados):
    r = client.get(f"/relatorios/turma/{dados['turma_id']}/csv", headers=h_gestor)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers.get("content-disposition", "")
    assert "9A" in r.text


def test_endpoint_pdf(client, h_gestor, dados):
    r = client.get(f"/relatorios/turma/{dados['turma_id']}/pdf", headers=h_gestor)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"


def test_export_aluno_barrado(client, h_aluno, dados):
    tid = dados["turma_id"]
    assert client.get(f"/relatorios/turma/{tid}/csv", headers=h_aluno).status_code == 403
    assert client.get(f"/relatorios/turma/{tid}/pdf", headers=h_aluno).status_code == 403


def test_export_turma_inexistente(client, h_gestor):
    assert client.get("/relatorios/turma/99999/csv", headers=h_gestor).status_code == 404
    assert client.get("/relatorios/turma/99999/pdf", headers=h_gestor).status_code == 404
