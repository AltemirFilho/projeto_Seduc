# Continuação — Frontend do SEDUC Simulados (handoff para outro chat)

> Cole o **prompt do fim deste arquivo** num chat novo. O chat novo **não** lembra da conversa
> anterior — tudo que importa está aqui, no `STATUS.md`, no `design_brief.md` e no `CLAUDE.md`.

## Estado atual (2026-06-25): frontend essencialmente completo

SPA React **construída por Claude, em código, conectada ao backend real** — não é mockup.
Quase todas as telas do `design_brief.md §6` estão prontas e **verificadas no browser** contra o
backend. Falta **1 tela real (C11 Turma detalhe)**; o resto é gap de backend ou `[fase futura]`.

## Onde está tudo

- **Frontend (este projeto):** `C:\Users\jusce\Documents\seduc-frontend\` — projeto Vite real (já com
  `node_modules`, build limpo). Stack: **React 18 + Vite + TS + Tailwind v4 (config CSS-first `@theme`)
  + React Router v6 + TanStack Query v5 + cliente HTTP tipado com JWT**. Fontes Baloo 2 / Nunito Sans
  via `@fontsource`. Tudo clay próprio (sem lib de UI).
  - `src/components/clay/` — primitivos (Button, Card, Input, Select, Textarea, Field, StatCard,
    StatusBadge, ConfirmDialog, Skeleton, Spinner).
  - `src/components/shell/` — Sidebar (genérico gestão+aluno), Topbar, GestaoLayout, AlunoLayout, ícones.
  - `src/lib/api/` — client (injeta Bearer, normaliza erro), e por domínio: auth, questoes, simulados,
    turmas, etiquetas, usuarios, relatorios, ia, provas. `src/lib/simuladosLocais.ts` = stopgap (ver gap).
  - `src/auth/` — AuthContext + guards (RequireAuth/RequireGestao/RequireAluno). `src/i18n/pt-BR.ts` =
    todos os textos. `src/pages/` — public / app (aluno) / gestao.
- **Backend (IMPORTANTE — usar o COMPLETO):** o backend completo está na branch
  **`origin/feat/backend-completo`** do repo `github.com/AltemirFilho/projeto_Seduc`. O checkout
  "normal" em `C:\Users\jusce\Documents\seduc-questoes` (branch `feat/relatorios-gestao`) está
  **DEFASADO** — não use pra rodar. Há um **git worktree** já montado:
  `C:\Users\jusce\Documents\seduc-completo` (branch `backend-completo`).

## Como rodar

```powershell
# 1) Backend completo (worktree) em :8000 — venv de seduc-questoes já tem anthropic+scikit-learn+reportlab
$py = "C:\Users\jusce\Documents\seduc-questoes\.venv\Scripts\python.exe"
cd C:\Users\jusce\Documents\seduc-completo
# (já migrado/seedado; se precisar recriar: & $py -m alembic upgrade head ; & $py scripts\seed_completo.py)
& $py -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000

# 2) Frontend em :3000
cd C:\Users\jusce\Documents\seduc-frontend
npm run dev        # http://localhost:3000  (CORS do backend libera :3000)
```

Demo (senha `sedu123`): `admin@`, `gestor@`, `suporte@`, `aluno@sedu.se.gov.br` (+ aluno02..aluno30).
Seed: 30 questões de Matemática, turmas 9A/9B/9C, 30 alunos, 15 simulados (finalizados/liberados/etc).
IA: risco aluno 1=baixo / 7=alto (sklearn sempre roda); diagnóstico simulado 1 (degrada p/ fallback
sem chave Claude — selo "automático").

## Verdade de fio do auth (NÃO inventar)

O backend **não usa 401** — toda falha de auth é **403**: login errado=`credenciais_invalidas`,
token inválido/expirado=`token_invalido`, sem perfil=`perfil_insuficiente`/`sem_permissao`, token
ausente=`{detail:"Not authenticated"}` cru. O cliente decide pelo **`codigo`**, não pelo status.
Rotas **sem prefixo `/api`** (raiz). Listas = envelope `{dados,meta}`; recurso único = flat.
Erros `{codigo,mensagem}`. Perfis crus: `admin`/`gestor`/`aluno`/`suporte`.

## O ÚNICO gap de backend que permanece

**`GET /simulados` (listar todos os simulados) não existe** — nem no backend-completo. Por isso a
lista de simulados (gestão C7 e aluno B2) usa `src/lib/simuladosLocais.ts` (localStorage dos
simulados criados nesta máquina). **Combinar `GET /simulados` com o Altemir.** (Todos os outros
"gaps" antigos — `/usuarios`, `GET/PATCH /questoes/{id}`, `/meu-resultado`, `/relatorios`, `/ia/*`,
export — **EXISTEM** no backend-completo.)

## O que falta (ver checklist em STATUS.md)

1. **C11 — Turma (detalhe)** `/gestao/turmas/:id` → única tela real não feita. Dados existem:
   `GET /usuarios?turma_id={id}` (alunos), `GET /relatorios/turma/{id}` (desempenho),
   `GET /ia/risco/{aluno_id}` (chip de risco por aluno). Linkar a partir da TurmasPage.
2. **C9 Monitorar simulado** — gap (sem endpoint de monitoramento); só mock se quiser.
3. **A1 Portal / A2 Como funciona** — hoje mínimas; enriquecer com as seções do brief (§A) se quiser.
4. **Versionar o frontend** (git init / repo) — ficou pendente "a decidir com o Altemir".
5. `[fase futura]` (A4/A5, C17–C20) — opcionais, sem backend.

## Cuidados conhecidos (Windows / este projeto)

- `preview_click` do harness às vezes não dispara submit/navegação SPA — verificar com
  `requestSubmit()`/`.click()` via eval. Deletar arquivo deixa o HMR do Vite sujo → reiniciar o preview.
- `EmConstrucaoPage.tsx` ficou órfão (nenhuma rota importa) — pode apagar.
- Memória do Claude tem `[[seduc-frontend]]` com o histórico detalhado.

---

## ▶ Prompt para colar no chat novo

```
Vamos continuar o frontend do SEDUC Simulados (você que faz, conectado ao backend real).
Ele está quase completo. Leia, em C:\Users\jusce\Documents\seduc-frontend: CONTINUATION_PROMPT.md
(estado atual + como rodar + o único gap GET /simulados), STATUS.md (checklist tela a tela),
CLAUDE.md e design_brief.md (§6 telas, §3 design clay). O backend COMPLETO roda do worktree
C:\Users\jusce\Documents\seduc-completo (branch backend-completo) em :8000 — NÃO use o checkout
defasado em seduc-questoes. Suba o backend e o Vite (:3000), confirme que o app sobe logando como
gestor (gestor@sedu.se.gov.br / sedu123). Depois, plano antes de código: construa a tela que falta
C11 (Turma detalhe em /gestao/turmas/:id — alunos da turma via /usuarios?turma_id, desempenho via
/relatorios/turma/{id}, chip de risco por aluno via /ia/risco/{id}), linkada a partir da lista de
Turmas. Mantenha o estilo claymorphism e os padrões já estabelecidos (cliente tipado, guards,
i18n pt-BR centralizado, estados loading/vazio/erro, AA). Verifique no browser ao terminar.
```
