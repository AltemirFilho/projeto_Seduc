from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.routers import (
    demo,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(etiquetas.router)
app.include_router(questoes.router)
app.include_router(importacao.router)
app.include_router(provas.router)
app.include_router(simulados.router)
app.include_router(respostas.router)
app.include_router(demo.router)

_DEMO_PATH = Path(__file__).resolve().parent.parent / "static" / "demo.html"


@app.get("/", response_class=HTMLResponse, tags=["demo"])
def home() -> str:
    return _DEMO_PATH.read_text(encoding="utf-8")


@app.get("/health", tags=["status"])
def health() -> dict:
    return {"projeto": "SEDUC Simulados — Banco de Questões", "status": "online"}
