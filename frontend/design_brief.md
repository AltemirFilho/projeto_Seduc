# SEDUC Simulados — Design Brief & Build Spec (frontend)

> Spec para **construir o frontend em código (por Claude), conectado ao backend FastAPI + banco** —
> não apenas mockups. Estilo visual: **claymorphism**. Estrutura/fluxos: inspirados no modelo
> *AvaliaEdu* (modelo de telas/IA, **não** referência visual). UI em **pt-BR**.
> Produto: **SEDUC Simulados** (SEDUC-SE).

---

## 0. Como usar — stack e fluxo de build

**Decisão:** o front é **construído por Claude** como SPA real, ligado à API (não Claude Design).

- **Stack:** React + Vite + TypeScript + Tailwind CSS (tokens clay do §3 como CSS vars/preset) +
  React Router + TanStack Query (estado de servidor) + cliente HTTP tipado com JWT. Componentes clay
  próprios — o preview vivo está em `tokens-preview.html`.
- **Locais:** front em `C:\Users\jusce\Documents\seduc-frontend\`; backend em
  `C:\Users\jusce\Documents\seduc-questoes\` (subir: `uvicorn app.api.main:app --reload` → `:8000`, Swagger `/docs`).
- **Conexão:** base em `VITE_API_URL`; toda chamada manda `Authorization: Bearer <token>`; tratar
  envelope `{dados,meta}` e erros `{codigo,mensagem}`; o CORS do backend libera `localhost:3000` /
  `127.0.0.1:3000` (rodar o Vite nessa porta **ou** ajustar `SEDU_CORS_ORIGINS` no `.env` do backend).
- **Por tela (§6):** implementar com §3 (design system) + §4 (shell do papel) + a spec (objetivo ·
  papel · rota · layout · dados/endpoint · estados loading/vazio/erro · interações · responsivo).
- ⚠️ **gap de backend** → usar **mock** com `// TODO: ligar endpoint` (§9), combinar com o Altemir.
  **[fase futura]** = tela sem backend; implementar só se quiser o conjunto completo.

**Ordem de build:** setup (Vite+Tailwind+tokens clay+router+api client+auth/guards) → **Login** → shell +
**Dashboard da gestão** → **Banco de questões** → **Simulados** (criar→gerar→preview→liberar→finalizar) →
**Aluno** (lista→responder→resultado) → **Relatórios + IA** → telas restantes.

---

## 1. Produto, usuários e papéis

**SEDUC Simulados** é a plataforma web de **simulados educacionais** da SEDUC-SE: banco de questões
etiquetadas → geração de provas balanceadas → ciclo do simulado (criar → gerar → liberar → aluno
responde → corrige) → **relatórios e diagnóstico por IA**.

Papéis (colapsados conforme o backend — não há "professor"):

| Papel | Quem | O que faz |
|---|---|---|
| **Público** | não autenticado | portal, como funciona, login |
| **Aluno** | `perfil = aluno` | vê simulados liberados, responde, vê o próprio resultado |
| **Gestão** | `perfil = gestor / admin` (suporte = leitura) | banco de questões, provas/simulados, turmas, usuários, relatórios e IA |

> A referência separa "professor" e "gestor"; aqui os dois viram **um único painel de Gestão**,
> porque o backend trata tudo via `gestor`/`admin`.

---

## 2. Backend — fonte de verdade dos dados

- **Base:** `${VITE_API_URL}` (ex.: `http://127.0.0.1:8000`). Docs vivas em `/docs` (Swagger).
- **Auth:** JWT no header `Authorization: Bearer <token>` (obtido no login). Sem token → 401; sem
  permissão → 403. Identidade do usuário **vem sempre do token**, nunca de campo na tela.
- **Listas paginadas:** envelope `{ "dados": [...], "meta": { pagina, porPagina, total, totalPaginas } }`.
- **Erros:** `{ "codigo": "...", "mensagem": "..." }` (404 `nao_encontrado`, 409 `regra_negocio`/
  `email_em_uso`/`questao_em_uso`/`simulado_nao_finalizado`, 422 `dados_invalidos`, 403 `sem_permissao`).

**Endpoints (todos já existem no backend, exceto onde marcado ⚠️):**

| Domínio | Método · rota | Uso na UI |
|---|---|---|
| Auth | `POST /auth/login` · `GET /auth/me` | login · perfil/sessão |
| Etiquetas | `GET /etiquetas/{series,materias,niveis,conteudos}` | selects/filtros |
| Questões | `GET /questoes` (filtros+paginação) · `POST /questoes` · `GET /questoes/{id}` · `PATCH /questoes/{id}` · `POST /questoes/importar` | banco, criar, ver, editar, importar JSON |
| Provas | `POST /provas/gerar` | gerar prova avulsa (sorteio balanceado + embaralhamento) |
| Simulados | `POST /simulados` · `POST /simulados/{id}/gerar` (curadoria IA c/ fallback) · `GET /simulados/{id}/preview` · `POST /simulados/{id}/liberar` · `GET /simulados/{id}/questoes` (sem gabarito) · `POST /simulados/{id}/finalizar` · `DELETE /simulados/{id}/questoes/{qid}` · `POST /simulados/{id}/questoes/{qid}/trocar` | ciclo completo do simulado |
| Respostas | `POST /respostas` (autosave) | aluno respondendo |
| Resultado | `GET /simulados/{id}/meu-resultado` (só após FINALIZADO) | resultado do aluno |
| Relatórios | `GET /relatorios/turma/{id}` · `/csv` · `/pdf` | relatório de desempenho da turma |
| Usuários | `POST /usuarios` · `GET /usuarios` (filtra turma/perfil, paginado) | cadastrar/listar |
| Turmas | `GET /turmas` | listar turmas |
| **IA** | `GET /ia/risco/{aluno_id}` · `GET /ia/diagnostico/{simulado_id}` | risco de evasão · diagnóstico da turma |

⚠️ **Gaps conhecidos (usar mock + ver §9):** não há `GET /simulados` (listar simulados), nem lista
de simulados disponíveis para o aluno, nem `GET /turmas/{id}`, nem agregados de dashboard.

**Estados do simulado:** `RASCUNHO → GERADO → LIBERADO → FINALIZADO` (cada um tem cor/badge — §5).

---

## 3. Estilo: Claymorphism (design system)

**Conceito:** superfícies "fofas", infladas, muito arredondadas, separadas por **sombra dupla**
(não por bordas). Macio e tátil, mas **institucional e legível** (é educação pública — nada de
brinquedo: contraste de texto forte, hierarquia clara).

### 3.1 Cores — paleta SEDUC (do cliente)

| Nome | Hex | Papel na UI |
|---|---|---|
| **Deep blue** | `#182350` | primário: CTA, nav ativo, **sidebar da gestão**, títulos e texto forte |
| **Powder blue** | `#AFD2FA` | secundário/info: seleção, chips, realces suaves, gráficos |
| **Floral white** | `#FEFAEF` | **fundo base** (o "barro" quente) e superfícies |
| **Pale brown** | `#B9915E` | acento quente: destaques, "ouro", atenção/pendente |

```
--bg:             #FEFAEF   /* floral white — base quente (o "barro") */
--surface:        #FFFFFF   /* card elevado */
--surface-sunken: #F5EFDA   /* campo / segmented afundado (creme) */
--primary:        #182350   /* deep blue — CTA, nav ativo, sidebar */
--primary-hover:  #243463
--on-primary:     #FEFAEF   /* texto/ícone sobre o azul (creme) */
--secondary:      #AFD2FA   /* powder blue — info / seleção */
--secondary-ink:  #1E3A6B   /* azul forte p/ texto sobre powder blue */
--accent:         #B9915E   /* pale brown — acento quente */
--accent-ink:     #6E5226   /* marrom forte p/ chip / texto */
--text:           #182350   /* deep blue como texto principal (AA sobre creme) */
--text-muted:     #6F6A5C   /* taupe — texto secundário */
--line:           #ECE5D3   /* divisória sutil (clay separa por sombra, não borda) */

/* Semânticas — a paleta-mãe não tem verde/vermelho; estas harmonizam com o quente */
--success: #4F9D6B   --warning: #B9915E   --danger: #C75D52   --info: #AFD2FA

/* Status do simulado */
--st-rascunho:#9A927E  --st-gerado:#5E86C2  --st-liberado:#4F9D6B  --st-finalizado:#182350
/* Risco de evasão */
--risco-baixo:#4F9D6B  --risco-medio:#B9915E  --risco-alto:#C75D52
```
**Uso & contraste (AA):** texto principal = **deep blue sobre creme** (alto contraste). Botão
primário = deep blue preenchido + texto **creme** (`--on-primary`). **Powder blue** e **pale brown**
são claros/médios → use como **fundo de chip/badge com texto na cor forte** (`--secondary-ink`,
`--accent-ink`), **nunca** com texto branco (reprova AA). Chips de status = fundo com ~15% de tint da
cor + texto na cor forte. Tema escuro (opcional): base `#182350`, superfícies `#20305F`, texto creme,
acentos powder blue + pale brown.

### 3.2 A assinatura clay — sombras
```
/* card/elemento "puffy" elevado — lado escuro com tint deep-blue (quente/coeso, não cinza) */
--clay:        12px 12px 28px rgba(24,35,80,.16),
               -10px -10px 24px rgba(255,255,255,.95),
               inset 2px 2px 3px rgba(255,255,255,.6),
               inset -3px -3px 6px rgba(24,35,80,.08);
--clay-sm:     6px 6px 14px rgba(24,35,80,.14), -6px -6px 12px rgba(255,255,255,.92);
/* estado pressionado / input em foco (afundado) */
--clay-inset:  inset 4px 4px 10px rgba(24,35,80,.16), inset -4px -4px 10px rgba(255,255,255,.95);
```
Regra: **superfícies elevadas usam `--clay`; campos/segmented/abas selecionadas e botões
pressionados usam `--clay-inset`.** Evitar bordas; usar sombra. Hover = elevar levemente
(aumentar blur ~10%). Foco de teclado = anel `--primary` 2px (acessibilidade, além da sombra).

### 3.3 Raios, espaço, tipografia
- **Raios:** card 24px · botão 16px (CTA principal pode ser pílula 999px) · input 14px · chip 999px · avatar 999px.
- **Espaço (4-base):** 4·8·12·16·24·32·48. Cards "respiram": padding 24–28. Gaps generosos.
- **Tipografia:** títulos em fonte arredondada (**"Baloo 2"** ou "Quicksand"); corpo em **"Nunito Sans"**
  (ou Inter). Escala: display 32/40 · h1 28 · h2 22 · h3 18 · corpo 16 · small 14 · caption 12.
  Peso: títulos 600–700, corpo 400–500.

### 3.4 Componentes (todos em clay)
- **Botões:** `primary` (preenchido `--primary`, texto branco, `--clay-sm`, pressiona com `--clay-inset`);
  `secondary` (surface + texto primary-strong); `ghost` (sem sombra, só hover); `danger`. Tamanhos sm/md/lg.
  Ícone+texto. Estados: hover, foco (anel), disabled (opacidade .5, sem sombra), loading (spinner).
- **Campos:** input/select/textarea com `--surface-2` afundado (`--clay-inset`), label acima, helper/erro abaixo
  (erro em `--danger`). Toggle/checkbox/radio "puffy". Date picker e dropdown como cards clay flutuantes.
- **Card / StatCard:** card clay; **StatCard** = ícone em "pílula" colorida + número grande + label + delta opcional.
- **Tabela:** sem grid pesado; linhas como faixas com leve elevação no hover; cabeçalho em `--text-muted`;
  ações na última coluna; densidade confortável. Paginação clay (pílulas).
- **Badge/Chip de status:** fundo pastel + texto na cor forte (mapa de status acima).
- **Abas / segmented control:** trilho afundado, item ativo "saltado" (`--clay-sm`).
- **Modal/Drawer:** card clay grande, overlay `rgba(24,35,80,.42)` (deep blue) desfocado.
- **Toast:** card clay no canto, ícone de status colorido.
- **Gráficos:** barras com cantos arredondados + sombra macia; donut/anel de progresso com trilho claro;
  paleta = cores de status/categorias. Sem gridlines duras.
- **Estados de coleção:** **loading** (skeletons clay pulsando), **vazio** (ilustração leve + CTA),
  **erro** (card com `--danger` + “tentar de novo”).

### 3.5 Acessibilidade (não negociável)
- Texto sempre AA+ (clay é pastel — **nunca** texto claro sobre pastel claro; usar `--text`/cor forte).
- Foco visível por teclado (anel), navegação por tab, labels associadas, `aria-*` em modais/abas/toasts.
- Alvo de toque ≥ 44px. Animações suaves e curtas; respeitar `prefers-reduced-motion`.

---

## 4. Shells e navegação

**4.1 Shell Público** — topbar (logo "SEDUC Simulados" + menu: Início · Como funciona · Entrar) e footer
institucional. Conteúdo centralizado, largura ~1100px.

**4.2 Shell Aluno** — sidebar clay estreita (ícone+label): **Início · Meus simulados · Resultados · Perfil**;
topbar com nome/avatar e sair. Conteúdo em cards.

**4.3 Shell Gestão** — sidebar clay com grupos:
- **Visão geral** → Dashboard
- **Conteúdo** → Banco de questões · Importar
- **Avaliações** → Simulados · Gerar prova · Calendário [fase futura]
- **Pessoas** → Turmas · Usuários
- **Inteligência** → Relatórios · Diagnóstico (IA) · Risco de evasão (IA)
- **Conta** → Perfil
Topbar: busca global, sino, avatar/perfil. Item ativo "saltado" (clay).

**Rotas** (sugestão): `/` `/como-funciona` `/login` · `/app` (aluno: `/app/simulados` `/app/simulados/:id/responder` `/app/resultados/:id` `/app/perfil`) · `/gestao` (`/gestao/questoes` `/gestao/questoes/nova` `/gestao/questoes/:id` `/gestao/simulados` `/gestao/simulados/novo` `/gestao/simulados/:id` `/gestao/gerar-prova` `/gestao/turmas` `/gestao/turmas/:id` `/gestao/usuarios` `/gestao/usuarios/novo` `/gestao/relatorios` `/gestao/ia/diagnostico/:simuladoId` `/gestao/ia/risco/:alunoId` `/gestao/perfil`).

---

## 5. Componentes compartilhados (referência rápida)
- **Sidebar / Topbar** (por papel, §4).
- **StatCard** (KPI), **DataTable** (+ filtros + paginação), **FormLayout** (label-acima, seções, ações fixas no rodapé),
  **StatusBadge** (estados do simulado e de risco), **FiltroBar** (selects de série/matéria/conteúdo/nível via `/etiquetas/*`),
  **Paginação**, **EmptyState/LoadingSkeleton/ErrorState**, **ConfirmDialog** (ações destrutivas: liberar, finalizar, excluir),
  **Toast**, **Breadcrumb**.

---

## 6. Telas

### A. Público

**A1 · Portal público** — `/` · Público
- **Layout:** hero clay (título "Portal de simulados, avaliações e desempenho", subtítulo, CTAs *Entrar* e *Como funciona*) + faixa de **3–4 StatCards** (nº de simulados, questões no banco, escolas/turmas — ⚠️ mock/estático) + seção "Acesso rápido" (cards: Entrar como aluno, Banco de questões, etc.) + "Destaques".
- **Dados:** estático (números podem ser mock). **Estados:** n/a. **Responsivo:** hero empilha; cards 1-col no mobile.

**A2 · Como funciona** — `/como-funciona` · Público
- Passos numerados (1 cadastro/login → 2 simulado liberado → 3 responder → 4 resultado/diagnóstico), cards por papel (Aluno / Gestão), FAQ. Estático.

**A3 · Entrar no sistema (login)** — `/login` · Público
- **Layout:** split — painel **deep blue (#182350)** à esquerda (marca + frase) + **card de login** à direita: e-mail, senha, botão *Entrar*, link "esqueci a senha" [fase futura], aviso de erro.
- **Dados:** `POST /auth/login {email, senha}` → guarda token, redireciona por perfil (aluno→`/app`, gestor/admin→`/gestao`).
- **Estados:** loading no botão; erro 401 → "e-mail ou senha inválidos" (não revelar qual). **A11y:** foco inicial no e-mail; Enter envia.

*[fase futura]* **A4 Notícias e editais**, **A5 Calendário público + validação de certificado** — sem backend; gerar só com mock.

### B. Aluno

**B1 · Dashboard do aluno** — `/app` · Aluno
- **Seções:** saudação + 3 StatCards (simulados liberados, média geral, pendentes — ⚠️ derivar de mock até listar); **"Próximos / disponíveis"** (lista de simulados liberados da turma) com CTA *Responder*; **"Desempenho recente"** (mini-gráfico + últimas notas).
- **Dados:** lista de simulados liberados ⚠️ **gap** (não há endpoint — mock; ver §9); notas via `GET /simulados/{id}/meu-resultado` (só finalizados).
- **Estados:** vazio ("nenhum simulado liberado ainda").

**B2 · Meus simulados e notas** — `/app/simulados` · Aluno
- **Layout:** abas **Disponíveis / Finalizados**. Disponíveis: cards (título, matéria(s), nº questões, prazo) → *Responder*. Finalizados: tabela (simulado, data, nota/percentual, status) → *Ver resultado*.
- **Dados:** ⚠️ lista (mock/gap); resultado por `GET /simulados/{id}/meu-resultado`.

**B3 · Realizar simulado** — `/app/simulados/:id/responder` · Aluno
- **Layout:** topo com título + **timer** + progresso (X de N); **uma questão por vez** (enunciado + alternativas em cards clay selecionáveis, **sem gabarito**); navegador lateral de questões (grid de bolinhas: respondida/atual/pendente); rodapé *Anterior / Próxima / Entregar*.
- **Dados:** `GET /simulados/{id}/questoes` (sem gabarito) para montar; **autosave** a cada escolha via `POST /respostas { simulado_id, questao_id, alternativa_id }` (identidade do aluno vem do token). *Entregar* = confirma (a correção/finalização é da gestão).
- **Estados:** salvar/“salvo” discreto; offline/erro de save → re-tentar; confirmação ao entregar; bloquear se simulado não estiver LIBERADO.

**B4 · Resultado do simulado** — `/app/resultados/:id` · Aluno
- **Layout:** cabeçalho com **nota/percentual** (anel de progresso clay) + acertos/erros/total; lista por questão (acertou ✓/✗, sua resposta, **gabarito**) ; bloco "pontos a melhorar" (conteúdos com mais erro).
- **Dados:** `GET /simulados/{id}/meu-resultado`. **Importante:** só disponível com simulado **FINALIZADO**; se não, a API retorna **409 `simulado_nao_finalizado`** → mostrar estado "resultado sai após o encerramento" (gabarito **não** aparece antes). *(Certificado = [fase futura].)*

### C. Gestão (gestor/admin)

**C1 · Dashboard da gestão** — `/gestao` · Gestão
- **Seções:** faixa de StatCards (questões no banco, simulados ativos, turmas, alunos — ⚠️ agregados são **gap**; mock ou derivar de `meta.total` das listas); "Ações rápidas" (Nova questão, Novo simulado, Cadastrar usuário); blocos de **indicadores** (desempenho por matéria — barras clay) e **alertas** (alunos em risco — via IA).
- **Dados:** `GET /questoes?...` `meta.total`, `GET /usuarios`, `GET /turmas`; risco via `GET /ia/risco/{aluno_id}`.

**C2 · Banco de questões** — `/gestao/questoes` · Gestão
- **Layout:** **FiltroBar** (série, matéria, conteúdo, nível — de `/etiquetas/*`) + busca + botão *Nova questão* e *Importar*; **DataTable** paginada (enunciado resumido, matéria, conteúdo, nível, nº alternativas, ações: ver/editar). Linha → C4.
- **Dados:** `GET /questoes?serie&materia&conteudo&nivel&pagina&por_pagina` (envelope `{dados,meta}`).
- **Estados:** vazio/sem resultados; loading skeleton de linhas.

**C3 · Criar questão (objetiva)** — `/gestao/questoes/nova` · Gestão
- **Layout:** form em seções: **Enunciado** (textarea); **Classificação** (selects série/matéria/conteúdo/nível via `/etiquetas/*`; matéria/conteúdo podem ser texto novo — backend cria); **Alternativas** (2–5, marcar **exatamente 1 correta**, reordenáveis); **Adaptações** (chips). Ações: Salvar / Cancelar.
- **Dados:** `POST /questoes { enunciado, serie, materia, conteudo, nivel, alternativas:[{texto,correta}], adaptacoes }`.
- **Validação:** 2–5 alternativas e 1 correta (422 `dados_invalidos` → realçar campo). *(Questão **dissertativa** = [fase futura]: backend é múltipla escolha.)*

**C4 · Ver / editar questão** — `/gestao/questoes/:id` · Gestão
- Igual ao C3, pré-preenchido; PATCH parcial (só o que mudou). **Regra:** trocar o conjunto de alternativas de uma **questão já respondida** retorna **409 `questao_em_uso`** → mostrar aviso e bloquear a troca (demais campos editáveis). Trocar matéria exige informar conteúdo.
- **Dados:** `GET /questoes/{id}` · `PATCH /questoes/{id}`.

**C5 · Gerar prova automática** — `/gestao/gerar-prova` · Gestão
- **Layout:** form de parâmetros (série, matéria(s), conteúdos, **distribuição por nível** com sliders que somam 100%, quantidade, seed opcional) → botão *Gerar*; resultado: prévia da prova (questões + gabarito, distribuição real) com *Regerar* / *Usar em um simulado*.
- **Dados:** `POST /provas/gerar { serie, materias, conteudos, distribuicao, quantidade, seed }` → prova (questões+gabarito+distribuição). Erros: 422 distribuição inválida; 409 `sem_questoes`.

**C6 · Criar / montar simulado** — `/gestao/simulados/novo` · Gestão
- **Layout:** passo 1 dados (título, **turma** via `/turmas`, parâmetros); passo 2 **gerar questões** (curadoria por IA com **fallback** clássico — mostrar badge "balanceado por IA" quando aplicável) ou montar manual; revisão.
- **Dados:** `POST /simulados {titulo, turma_id, parametros}` → `POST /simulados/{id}/gerar` (curadoria IA). Antes de liberar: `DELETE /simulados/{id}/questoes/{qid}` e `POST .../trocar` para ajustar.
- **Estados:** badge de **status** (RASCUNHO/GERADO). Curadoria IA pode cair em fallback → indicar discretamente.

**C7 · Simulados / Gestão de avaliações** — `/gestao/simulados` · Gestão
- **Layout:** DataTable de simulados (título, turma, status [badge], nº questões, datas, ações: ver/preview, liberar, finalizar, relatório). Filtro por status/turma. *Novo simulado*.
- **Dados:** ⚠️ **gap** — não há `GET /simulados`; usar **mock** até criar (§9). Ações reais: `/preview`, `/liberar`, `/finalizar`.
- **Interações:** **Liberar** e **Finalizar** abrem **ConfirmDialog** (ação irreversível de estado).

**C8 · Visualizar simulado (prévia com gabarito)** — `/gestao/simulados/:id` · Gestão
- Cabeçalho (título, turma, status, ações de ciclo) + lista de questões **com gabarito** + distribuição. Antes de liberar: remover/trocar questão.
- **Dados:** `GET /simulados/{id}/preview`; `DELETE .../questoes/{qid}`; `POST .../questoes/{qid}/trocar`; `POST .../liberar`; `POST .../finalizar`.

**C9 · Monitorar simulado** — `/gestao/simulados/:id?aba=monitor` · Gestão *(⚠️ gap — sem endpoint de monitoramento; mock)*
- Progresso da turma (quem entregou, % concluído), tempo médio. Deixar pronto para ligar quando houver endpoint.

**C10 · Turmas e alocação** — `/gestao/turmas` · Gestão
- StatCards (turmas, alunos, escolas) + DataTable de turmas (escola, série, ano, nº alunos, ações). *Nova turma* [fase futura: sem POST /turmas].
- **Dados:** `GET /turmas`. Contagem de alunos por turma via `GET /usuarios?turma_id=`.

**C11 · Turma (detalhe)** — `/gestao/turmas/:id` · Gestão
- Cabeçalho da turma + StatCards de desempenho + **lista de alunos** (com indicador de **risco** opcional) + atalho para **relatório** e **diagnóstico**.
- **Dados:** `GET /usuarios?turma_id={id}` (alunos), `GET /relatorios/turma/{id}` (desempenho), `GET /ia/risco/{aluno_id}` por aluno. ⚠️ `GET /turmas/{id}` não existe — usar item da lista de `/turmas`.

**C12 · Cadastrar / gerenciar usuário** — `/gestao/usuarios` e `/gestao/usuarios/novo` · Gestão
- **Lista:** DataTable de usuários (nome, e-mail, perfil [badge], turma, ações), filtros **turma**/**perfil**, paginação. **Form:** nome, e-mail, senha, **perfil** (aluno/gestor/admin/suporte), **turma** (obrigatória só p/ aluno).
- **Dados:** `GET /usuarios?turma_id&perfil&pagina&por_pagina`; `POST /usuarios`. **Regras:** e-mail único → **409 `email_em_uso`** (case-insensitive); aluno sem turma → 422; nunca exibir `senha_hash`.

**C13 · Relatórios e desempenho** — `/gestao/relatorios` · Gestão
- Seletor de **turma** → **relatório**: StatCards (alunos, respostas, média de acerto), **ranking de conteúdos por taxa de erro** (barras clay), tabela por conteúdo; botões **Exportar CSV / PDF**.
- **Dados:** `GET /relatorios/turma/{id}` (+ `/csv`, `/pdf` → download com `Content-Disposition`). Atalho para o **diagnóstico por IA** do simulado.

**C14 · Diagnóstico pedagógico (IA)** — `/gestao/ia/diagnostico/:simuladoId` · Gestão
- Resumo gerado por IA sobre o desempenho da turma num **simulado finalizado**: pontos fortes/fracos, recomendações; cards de tópicos. Selo "gerado por IA".
- **Dados:** `GET /ia/diagnostico/{simulado_id}` (exige simulado FINALIZADO). Estados: gerando/indisponível; erro de IA → mensagem amigável.

**C15 · Risco de evasão (IA)** — `/gestao/ia/risco/:alunoId` (e widget na turma) · Gestão
- Indicador de risco do aluno (anel/badge baixo/médio/alto) + fatores + recomendação.
- **Dados:** `GET /ia/risco/{aluno_id}` (calcula, salva e devolve). Mostrar como **chip de risco** na lista de alunos (C11) e detalhe aqui.

**C16 · Perfil da gestão** — `/gestao/perfil` · Gestão
- Dados da conta (`GET /auth/me`), preferências, sair. Edição de perfil = [fase futura] (sem PATCH /usuarios/me).

*[fase futura]* **C17 Calendário institucional · C18 Locais de prova · C19 Publicações e editais · C20 Certificados** — sem backend; gerar só com mock se quiser o conjunto do modelo.

---

## 7. Regras globais
- **Responsivo:** desktop-first (gestão é densa), mas tudo colapsa: sidebar → drawer no mobile; tabelas → cards empilhados; "Realizar simulado" é ótimo no celular (1 questão por tela).
- **Estados:** toda coleção tem loading (skeleton clay), vazio (ilustração + CTA) e erro (retry). Toda ação tem feedback (toast) e as destrutivas têm confirmação.
- **i18n:** textos em **pt-BR**, centralizados (sem string solta na tela). Datas/números pt-BR.
- **Permissão:** rotas de gestão exigem `gestor/admin`; aluno só acessa `/app`; guardar token e tratar 401 (redirect login) e 403 (tela "sem acesso").

## 8. Mapa tela → endpoint (resumo)
A3→`/auth/login` · B3→`/simulados/{id}/questoes`+`/respostas` · B4→`/simulados/{id}/meu-resultado` ·
C2→`/questoes` · C3→`POST /questoes` · C4→`GET/PATCH /questoes/{id}` · C5→`/provas/gerar` ·
C6/C8→`/simulados`+`/{id}/gerar|preview|liberar|finalizar|trocar` · C12→`/usuarios` · C13→`/relatorios/turma/{id}(/csv|/pdf)` ·
C14→`/ia/diagnostico/{id}` · C15→`/ia/risco/{id}` · C10/C11→`/turmas`+`/usuarios?turma_id`.

## 9. Backlog de backend (a UI usa mock até existir)
1. **`GET /simulados`** (listar/filtrar simulados por status/turma) — alimenta C7, C9 e o dashboard.
2. **Lista de simulados disponíveis para o aluno** (ex.: `GET /simulados?turma=me&status=liberado`) — B1/B2.
3. **Agregados de dashboard** (contagens/indicadores) — C1/B1 (hoje só via `meta.total` das listas).
4. **`GET /turmas/{id}`** e **`POST /turmas`** — C10/C11.
5. **Monitoramento de simulado em andamento** — C9.
6. **Edição do próprio perfil / trocar senha** — A3 (esqueci), C16.
> Combinar esses com o Altemir (alguns são Frente B / núcleo). Enquanto não existirem, gerar a tela
> com **dados mock** e marcar claramente `// TODO: ligar endpoint`.

---

## 10. Checklist por tela (ao implementar)
Para cada tela do §6, garanta:
- **Design system:** cores/sombras `--clay`/`--clay-inset`, raios grandes, tipografia arredondada, pt-BR, **AA**.
- **Shell/rota** do papel (§4) + **permissão** (guard por perfil; tratar 401→login, 403→sem acesso).
- **Dados** pelo endpoint da spec via TanStack Query (envelope `{dados,meta}`; erros `{codigo,mensagem}`).
- **Estados** loading (skeleton clay) / vazio / erro, e **responsivo** (sidebar→drawer, tabela→cards).
- **Sem inventar endpoint:** onde houver gap (§9), mock com `// TODO: ligar endpoint`.
