# Laudo Técnico — Sistema de Simulados Educacionais com IA (SEDUC-SE)

> Síntese da revisão técnica do backend, em tom de roadmap. **Os detalhes de segurança
> exploráveis (arquivo:linha de falhas, passos de exploração, payloads) NÃO ficam neste
> arquivo** — o repositório é público. Esse detalhe vive em nota local fora do versionamento
> (`REVIEW.seguranca.full.local.md`, no `.gitignore`) e no histórico de conversas da equipe.
> Aqui ficam só a leitura de arquitetura, o estado e o plano.

## 1. Visão geral

Backend bem pensado para o estágio de MVP acadêmico. A arquitetura em camadas
(API → Service → Repository → Model) é real e está bem aplicada no fluxo central — banco de
questões, geração de prova e ciclo de vida do simulado funcionam ponta a ponta, com regra de
negócio testável isolada do HTTP.

As frentes de evolução conhecidas são duas: **endurecimento de autorização** (sair da
autorização só por perfil para também isolar por dono/turma/escola do recurso) e
**alinhamento de contrato com o front** (que hoje roda em mocks). Nenhuma quebra o caminho
feliz da demonstração, mas ambas cobram juros conforme entram IA, relatórios e a integração
real com o front.

## 2. Pontos fortes (defender com orgulho)

- **Camadas reais no fluxo principal.** `provas.py`, `simulados.py`, `respostas.py`,
  `importacao.py` não importam SQLAlchemy nem montam query — delegam aos services, que não
  conhecem FastAPI. A seta API→Service→Model está limpa nesse caminho.
- **Repository isolando a query complexa.** `questao_repository.py` concentra o filtro
  multi-critério com joins + `selectinload` (evita N+1) e é reaproveitado por `prova_service`
  e `simulado_service` — exatamente o papel de um repositório.
- **Máquina de estados do simulado** (RASCUNHO→GERADO→LIBERADO→FINALIZADO) com guardas em
  cada transição. Impede liberar antes de gerar, responder antes de liberar etc.
- **Modelagem de dados madura.** SQLAlchemy 2.x (`Mapped`/`mapped_column`),
  `UniqueConstraints` de negócio e cascades corretos.
- **Segurança criptográfica bem feita.** PBKDF2-HMAC-SHA256 com 100k iterações + salt por
  usuário + `hmac.compare_digest`; JWT com algoritmo em allowlist e `exp` validado.
- **Geração determinística por seed**, com embaralhamento que preserva o vínculo do gabarito
  — ótimo para auditoria/reprodução.
- **Importação em lote robusta**: valida item a item, acumula erros por linha `{linha, motivo}`
  e só commita as válidas.
- **Acesso a dados via ORM parametrizado** — sem f-string em query, sem `text()` cru, sem
  `eval/exec/subprocess`. `.env` e `*.db` fora do git.

## 3. Arquitetura — avaliação honesta

A direção das dependências está **correta no caminho central**, que é o mais difícil de
acertar. O ponto de evolução é **consistência, não concepção**: nem todo acesso a dados passa
por repository (parte das queries ainda nasce inline em services e routers auxiliares). A
recomendação é padronizar extraindo as queries existentes para `*_repository.py`, mantendo o
estilo de `questao_repository` — é mover, não reescrever.

Política de transação: o **service é o dono da transação** (quem dá commit); o router nunca
commita. `get_session` faz rollback no except. Manter essa regra ao crescer.

## 4. Segurança — direção (sem detalhe explorável)

A **base criptográfica está sólida**; a frente de trabalho é **controle de acesso**. O tema
dominante é sair da autorização **só por perfil** (admin/gestor/aluno) para também isolar por
**propriedade do recurso** — dono do simulado, turma do aluno, e (quando houver schema)
escopo do gestor por escola/turma.

O endurecimento é incremental e já em andamento (isolamento por dono e por turma no ciclo do
simulado e nos endpoints derivados). Os achados específicos, seu passo a passo e o estado de
cada correção são rastreados **fora do versionamento** (nota local + conversas), conforme a
política de não publicar detalhe explorável em repositório público.

> **Higiene de repositório público:** evitar commitar laudo de vulnerabilidade com
> arquivo:linha e passo de exploração. Versões antigas deste arquivo no histórico ainda
> contêm esse detalhe; removê-las exige reescrever histórico (decisão à parte, com cuidado em
> repo já clonado/forkado).

## 5. Integração com o front

Hoje **não existe integração real**: o repo de front roda em mocks (MSW). Os dois lados foram
desenhados contra contratos com divergências em vários eixos (tipo de `id`, vocabulário
código vs. label PT, envelope de resposta, prefixo `/api`, token em header vs. cookie). A
serialização é centralizada, então alinhar o contrato é cirúrgico.

**Ação recomendada antes de telas novas:** um *spike de integração* — subir a FastAPI, apontar
um fluxo (listar questões) para o backend real, desligar o MSW desse fluxo e ver o que quebra.
Transforma a lista de divergências de teórica em priorizada.

## 6. Alinhamento ao backlog (feito vs. faltando)

**Entregue (MVP funcional):** FastAPI + SQLAlchemy 2.x; banco de questões + etiquetas
(série/matéria/conteúdo/nível); geração de prova balanceada e reprodutível; ciclo de simulado
com máquina de estados + correção/nota; importação em lote com relatório; auth (hash + JWT +
`/login` + `/me`) plugada por perfil; Alembic; testes (pytest); **IA**: curadoria embutida no
gerar (com fallback clássico), predição de risco (scikit-learn) e diagnóstico pedagógico
(Claude, com fallback).

**Faltando / próximas fases:** escopo de autorização por escola/turma (precisa de schema);
relatórios e exportação (PDF/CSV); migração efetiva para PostgreSQL/Redis; alinhamento de
contrato com o front; CI + proteção de branch.

## 7. Roadmap recomendado

**Curto prazo:**
1. Concluir o endurecimento de autorização por propriedade do recurso (dono/turma) e cobrir
   com testes de isolamento.
2. Decidir e modelar o escopo do gestor por escola/turma (schema) — cruza a fatia de
   relatórios/usuários; coordenar na equipe.
3. CI rodando `pytest` + proteção de branch (PR obrigatório para a `main`).

**Médio prazo:**
4. Fechar contrato canônico com o front + spike de integração.
5. Migração para Postgres: conferir índices, `JSONB`, `ondelete`, enums/timestamps com dump
   real.
6. Relatórios de turma (derivados de `Resposta`) → uma fase de cada vez.

## 8. O que dizer ao mentor

> "Construí um backend em camadas (API → Service → Repository → Model) com o fluxo central
> completo: banco de questões, geração de prova balanceada e reprodutível, e o ciclo de
> simulado com máquina de estados e correção. A modelagem usa SQLAlchemy 2.x com constraints,
> o auth tem hash forte (PBKDF2) e JWT por perfil, e há uma camada de IA (curadoria, predição
> de risco e diagnóstico) sempre com fallback.
>
> Sei onde estão as próximas frentes e as tenho priorizadas: **endurecer a autorização para
> isolar por dono/turma/escola do recurso** (não só por perfil), alinhar o contrato com o
> front (que hoje roda em mocks), e amadurecer prontidão (CI, proteção de branch, Postgres).
> Cada fraqueza é um item de roadmap consciente."
