# CLAUDE.md — Frontend do SEDUC Simulados

## Projeto
Frontend (SPA) do **SEDUC Simulados** (SEDUC-SE): consome o backend FastAPI (banco de questões →
provas/simulados → ciclo → relatórios + IA). **Construído por Claude, em código, conectado ao backend
real + banco.** UI em **pt-BR**, estilo **claymorphism**.

## Antes de qualquer tarefa, leia
0. **`STATUS.md`** — estado atual tela a tela (o que está pronto / a fazer). **`CONTINUATION_PROMPT.md`** —
   como rodar. ⚠️ O backend **COMPLETO** roda do **worktree `C:\Users\jusce\Documents\seduc-completo`**
   (branch `backend-completo`), NÃO do `seduc-questoes` (que está defasado).
1. `design_brief.md` — spec completa: design system clay (§3), telas (§6), endpoints (§2), gaps (§9).
2. `tokens-preview.html` — preview vivo do claymorphism (referência de UI).
3. `CONTINUATION_PROMPT.md` — contexto/handoff (stack, backend, paleta, ordem de build).
4. **O `CLAUDE.md` do backend** em `..\seduc-questoes\CLAUDE.md` — **regras de colaboração que valem
   aqui também**: time (Juscelino + Altemir), git workflow, **contrato da API** e "sem trailer do Claude".

## Stack & convenções
- **React + Vite + TypeScript + Tailwind CSS** + React Router + TanStack Query + cliente HTTP tipado com JWT.
- **Claymorphism próprio:** tokens do `design_brief.md §3` como CSS vars / preset do Tailwind; componentes
  clay próprios (sem lib de UI pesada). Contraste **AA** (powder blue e pale brown são claros → texto na
  cor forte, **nunca** branco).
- **UI em pt-BR**, centralizada (sem string solta). Código/identificadores em inglês.
- **Dados** sempre via TanStack Query; o cliente injeta `Authorization: Bearer <token>`; tratar envelope
  `{dados,meta}` e erros `{codigo,mensagem}` (401→login, 403→sem acesso, 404/409/422 com mensagem clara).
- Estados **loading (skeleton clay) / vazio / erro** em toda coleção; responsivo (sidebar→drawer, tabela→cards).

## Contrato da API — cuidado especial
Consome a **API real** do backend-completo. **Não invente campo nem endpoint.** ⚠️ Os "gaps" do
`design_brief.md §9` foram **quase todos resolvidos** no `feat/backend-completo` (`/usuarios`,
`GET/PATCH /questoes/{id}`, `/simulados/{id}/meu-resultado`, `/relatorios`+export, `/ia/*` já existem).
**Gaps reais que sobram:** `GET /simulados` (listar — hoje stopgap `src/lib/simuladosLocais.ts` em
localStorage) e monitoramento de simulado (C9). Combine esses com o Altemir antes de fixar contrato.

## Git & colaboração (herda do backend)
- Branch própria por tarefa; **nunca commitar direto na `main`**; PR pro outro revisar. *(Repo do front
  a definir com o Altemir — próprio ou junto.)*
- **Não** adicionar `Co-Authored-By: Claude` nem "Generated with Claude Code". Mensagem multi-linha: `git commit -F arquivo`.
- **Plano antes de código.** Mudança que afeta o contrato esperado, dependência nova pesada, ou decisão
  de arquitetura do front → **pare e confirme** com o operador.

## Máquina (Windows / PowerShell)
git-bash mangla acento passado como argumento (usar arquivo UTF-8 / `gh api --input`); ver o `CLAUDE.md`
do backend e a memória para os cuidados conhecidos.
