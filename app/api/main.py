"""Aplicação FastAPI — API do Banco de Questões (SEDUC Simulados).

Esta é a "casca" HTTP. A lógica de verdade está nas camadas:
    app/repositories/  -> acesso ao banco
    app/services/      -> regra de negócio (geração de prova)

Rodar localmente:
    uvicorn app.api.main:app --reload

Documentação interativa (Swagger) gerada automaticamente:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from app.api.routers import (
    etiquetas,
    importacao,
    provas,
    questoes,
    respostas,
    simulados,
)

app = FastAPI(
    title="SEDUC Simulados — API do Banco de Questões",
    description=(
        "Backend do Sistema de Simulados Educacionais com IA (SEDUC-SE). "
        "Endpoints para consultar etiquetas, filtrar questões e gerar provas."
    ),
    version="0.1.0",
)

app.include_router(etiquetas.router)
app.include_router(questoes.router)
app.include_router(importacao.router)
app.include_router(provas.router)
app.include_router(simulados.router)
app.include_router(respostas.router)


@app.get("/", tags=["status"])
def raiz() -> dict:
    """Healthcheck simples + atalho para a documentação."""
    return {
        "projeto": "SEDUC Simulados — Banco de Questões",
        "status": "online",
        "documentacao": "/docs",
    }
