# SEDUC Simulados — Frontend

SPA em **React + Vite + TypeScript + Tailwind v4**, estilo **claymorphism**, conectada ao
backend FastAPI real (`../seduc-questoes`). UI em pt-BR.

## Rodar localmente

1. **Backend** em `:8000` (em `../seduc-questoes`):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   uvicorn app.api.main:app --reload
   ```
   Usuários demo (senha `sedu123`): `admin@`, `gestor@`, `aluno@sedu.se.gov.br`.

2. **Frontend** (esta pasta):
   ```powershell
   npm install
   npm run dev        # http://localhost:3000  (porta liberada no CORS do backend)
   ```

Config: `VITE_API_URL` no `.env` (default `http://127.0.0.1:8000`, sem prefixo `/api`).

## Estado atual
- Scaffold: tokens clay, router, cliente HTTP tipado com JWT, contexto de auth + guards de rota.
- Tela de **Login** (`/login`) conectada ao `POST /auth/login`, com redirect por perfil.
- Demais telas (shells, dashboards, banco de questões, simulados, IA) seguem a ordem do `design_brief.md §6`.

## Convenções
- Identificadores em inglês/pt conforme o domínio; **textos de UI centralizados** em `src/i18n/pt-BR.ts`.
- Contraste **AA**: texto sempre na cor forte sobre pastel (nunca branco sobre powder/pale brown).
- Onde o backend tem **gap** (`design_brief §9`), usar mock com `// TODO: ligar endpoint` (combinar com o Altemir).
