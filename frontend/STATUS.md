# STATUS — Frontend SEDUC Simulados (2026-06-25)

Checklist das telas do `design_brief.md §6`. ✅ pronta+verificada · 🟡 mínima/parcial · ❌ a fazer ·
⛔ gap de backend · 💤 [fase futura].

## Público (`/`)
- ✅ **A3 Login** `/login` — `POST /auth/login`, redirect por perfil, erro 403 inline. `pages/public/LoginPage.tsx`
- ✅ **A1 Portal** `/` — hero + StatCards (exemplo) + Acesso rápido + Destaques, em shell público (topbar+rodapé). `PortalPage.tsx` + `shell/PublicLayout.tsx`
- ✅ **A2 Como funciona** `/como-funciona` — passos numerados + cards por papel + FAQ (accordion). `ComoFuncionaPage.tsx`
- 💤 A4 Notícias/editais · A5 Calendário/certificado

## Aluno (`/app`, shell `AlunoLayout`)
- ✅ **B1 Início** `/app` — saudação + KPIs + disponíveis (lista real `GET /simulados/disponiveis`). `pages/app/AlunoInicioPage.tsx`
- ✅ **B2 Meus simulados** `/app/simulados` — abas disponíveis/finalizados (lista real `GET /simulados/disponiveis`). `MeusSimuladosPage.tsx`
- ✅ **B3 Responder** `/app/simulados/:id/responder` — 1 questão/tela, **autosave `POST /respostas`**. `ResponderPage.tsx`
- ✅ **B4 Resultado** `/app/resultados/:id` — `GET /simulados/{id}/meu-resultado` (nota + por questão). `ResultadoAlunoPage.tsx`
- ✅ Perfil `/app/perfil` — `PerfilAlunoPage.tsx`

## Gestão (`/gestao`, shell `GestaoLayout`)
- ✅ **C1 Dashboard** `/gestao` — KPIs reais (questões/turmas/alunos) + distribuição por matéria. `DashboardPage.tsx`
- ✅ **C2 Banco de questões** `/gestao/questoes` — FiltroBar + DataTable paginada. `QuestoesPage.tsx`
- ✅ **C3 Criar questão** `/gestao/questoes/nova` — `POST /questoes`. `NovaQuestaoPage.tsx` + `QuestaoForm.tsx`
- ✅ **C4 Ver/Editar questão** `/gestao/questoes/:id` (+`/editar`) — `GET/PATCH`, 409 `questao_em_uso`. `QuestaoDetalhePage.tsx` / `EditarQuestaoPage.tsx`
- ✅ **C5 Gerar prova** `/gestao/gerar-prova` — `POST /provas/gerar`, prévia+gabarito. `GerarProvaPage.tsx`
- ✅ **C6 Criar simulado** `/gestao/simulados/novo` — `POST /simulados`+`/gerar`. `NovoSimuladoPage.tsx`
- ✅ **C7 Simulados** `/gestao/simulados` — lista real `GET /simulados` (filtro por status). `SimuladosPage.tsx`
- ✅ **C8 Visualizar simulado** `/gestao/simulados/:id` — resumo via `GET /simulados/{id}` + preview+ciclo (liberar/finalizar/remover/trocar) + ConfirmDialog. `SimuladoDetalhePage.tsx`
- ✅ **C9 Monitorar simulado** `/gestao/simulados/:id?aba=monitor` — aba "Monitorar" na C8 com **dados reais** `GET /simulados/{id}/monitoramento` (KPIs, conclusão da turma, progresso por aluno). `MonitorSimulado.tsx`
- ✅ **C10 Turmas** `/gestao/turmas` — `GET /turmas`. `TurmasPage.tsx`
- ✅ **C11 Turma (detalhe)** `/gestao/turmas/:id` — cabeçalho (turma da lista `/turmas`) + KPIs/pontos de atenção (`/relatorios/turma/{id}`) + alunos (`/usuarios?turma_id`) com **chip de risco sob demanda** (botão → `/ia/risco/{aluno_id}` por aluno, usando o `aluno_id` agora exposto por `/usuarios`) + atalhos relatório (`?turma=`)/diagnóstico. Linkada da C10. `TurmaDetalhePage.tsx` + `clay/RiscoBadge.tsx`.
- ✅ **C12 Usuários** `/gestao/usuarios` (+`/novo`) — `GET/POST /usuarios`. `UsuariosPage.tsx` / `NovoUsuarioPage.tsx`
- ✅ **C13 Relatórios** `/gestao/relatorios` — `/relatorios/turma/{id}` + export CSV/PDF. `RelatoriosPage.tsx`
- ✅ **C14 Diagnóstico (IA)** `/gestao/ia/diagnostico/:simuladoId` — `/ia/diagnostico`, selo IA/fallback. `DiagnosticoPage.tsx`
- ✅ **C15 Risco de evasão (IA)** `/gestao/ia/risco/:alunoId` — `/ia/risco`. `RiscoPage.tsx`
- ✅ **C16 Perfil** `/gestao/perfil` — `PerfilGestaoPage.tsx`
- 💤 C17–C20 (calendário, locais, editais, certificados)

## Resumo
- **Telas reais a fazer:** **0**. A1/A2 enriquecidas; C7/C9/B1/B2 religados aos endpoints reais (2026-06-25).
- **Gaps de backend RESOLVIDOS** (branch `feat/listagem-simulados-monitor` em `seduc-completo`, commit 290e73e, pytest 92 verdes — **pendente PR pro Altemir**):
  - `GET /simulados` (gestão, filtra status/turma) + `GET /simulados/{id}` (resumo) + `GET /simulados/disponiveis` (aluno).
  - `GET /simulados/{id}/monitoramento` (progresso por aluno).
  - `/usuarios` agora expõe `aluno_id` → corrige o risco da C11/C15 (antes batia em `usuario.id` ≠ `aluno.id`; o "aluno 31 = 404" era esse mismatch, não seed).
  - Stopgap `simuladosLocais.ts` removido.
- **Pendente (precisa do Altemir):** merge do PR acima; versionar o repo do front (decisão de repo).
- **Restam só `[fase futura]`** (A4/A5, C17–C20) — opcionais, sem backend.
- `typecheck`/`build` (front) e `pytest` (back) limpos; tudo verificado no browser contra o backend-completo.
