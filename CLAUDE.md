# CLAUDE.md — Regras de colaboração do SEDUC Simulados

## Projeto
**SEDUC Simulados** (`projeto_Seduc`) é o **backend** do Sistema de Simulados Educacionais com IA da Secretaria de Educação de Sergipe (SEDUC-SE), projeto da Residência em Software (UNIT/ADS). Ele oferece: banco de **questões etiquetadas** (série / matéria / conteúdo / nível), **geração de provas balanceadas e reprodutíveis** (por seed), o **ciclo de vida do simulado** (RASCUNHO → GERADO → LIBERADO → FINALIZADO) com correção de nota, importação de questões em lote e **autenticação JWT por perfil** (admin, gestor, aluno, suporte).

- **Stack:** Python 3.11+ · **FastAPI** · **SQLAlchemy 2.x** (`Mapped`/`mapped_column`). **SQLite** no dev → **PostgreSQL** em produção (troca por `SEDU_DATABASE_URL`). **JWT** (PyJWT, HS256) com senha em PBKDF2. **Alembic** (migrações — fonte de verdade do schema) · **pytest** · **Docker**.
- **Fase atual:** MVP funcional do backend; o caminho central (questões → prova → simulado → correção) está completo e testado. As próximas frentes conhecidas estão no `REVIEW.md` e no `PLANO_EQUIPE.md` (contrato com o front, relatório de turma, IA de curadoria, migração efetiva para PostgreSQL/Redis). *Índices e variante JSONB já foram implementados no endurecimento — não reabra.*
- **Time:** Altemir `@AltemirFilho` (autor original do backend) e Juscelino `@Juscelinoo` (entrou em 2026-06-25). É trabalho **em dupla**. Este backend faz parte de uma residência com mais pessoas e um **frontend separado** (repo `simulados-sedu-frontend`), que hoje roda em **mocks (MSW)** — daí o cuidado redobrado com o contrato da API (ver seção própria).

## Contexto
Este repositório é desenvolvido por mais de um dev, cada um usando sua própria instância do Claude Code. Você é uma dessas instâncias. Existe outra instância sua trabalhando neste mesmo projeto em paralelo, com outro operador. Vocês não compartilham contexto entre si — só o que está versionado neste repositório.

Sua prioridade não é só escrever bom código. É escrever código que se integre limpo ao que o outro lado está fazendo, sem gerar retrabalho, conflito de estilo ou decisões arquiteturais divergentes.

## Antes de qualquer tarefa, leia
1. `README.md` — visão geral, como rodar, variáveis de ambiente, modelo de dados.
2. `PLANO_EQUIPE.md` — divisão atual do trabalho em frentes e quem toca o quê.
3. `REVIEW.md` — laudo técnico (dívidas conhecidas, decisões, roadmap). Leia **uma vez** para se situar. ⚠️ Boa parte dos achados **CRÍTICO/ALTO já foi corrigida** (autorização plugada, fail-fast no segredo, Alembic, testes, deploy) — **não reabra achado já resolvido**; confira o código atual antes.
4. O **módulo/camada** onde a tarefa vai acontecer, para casar com o estilo existente.

Se algo essencial para a tarefa estiver vago ou ausente, **pare e avise** antes de codar.

> **Arquivos companheiros (opcional):** este CLAUDE.md é autossuficiente. Se o time quiser adotar o sistema multi-arquivo (`EDITING.md` para anti-colisão, `DECISIONS.md` para log de decisões, `TODO.md` para dívidas), combinem antes — não invente esses arquivos sozinho.

## A arquitetura em camadas é a regra central
O maior valor deste backend — e o ponto em que o `REVIEW.md` cobra consistência — é a separação em camadas. **Respeite a direção das dependências:**

```
HTTP → app/api/routers/   validação (Pydantic), autorização (Depends), serialização.
                          NUNCA importa SQLAlchemy. NUNCA dá commit.
       app/services/      regra de negócio + máquina de estados. É o DONO da transação (quem dá commit).
       app/repositories/  acesso a dados: monta os select()/joins/selectinload.
                          Espelhe o estilo de questao_repository.py.
       app/models.py      ORM (SQLAlchemy 2.x).   app/database.py = engine/sessão.
```

Regras práticas:
- **Router não conhece ORM.** Precisa de dado? Chame um service, que chama um repository. Não monte `select(...)` no router.
- **Service é dono da transação.** O router nunca dá `sessao.commit()`. A sessão chega por `Depends(get_session)` (que já faz rollback no `except`).
- **Query nova vai no repository.** Ao estender, prefira adicionar método a um `*_repository.py` em vez de espalhar query no service/router. (Os routers atuais já seguem esse caminho — use `questao_repository.py` / `etiqueta_repository.py` como referência e mantenha o padrão no código novo.)
- **Erros de domínio** sobem como `app/exceptions.py` (`NaoEncontrado` 404, `RegraNegocio` 409, `DadosInvalidos` 422, `PermissaoNegada` 403); o handler central em `main.py` os converte em `{codigo, mensagem}`. Não devolva `HTTPException` cru se há uma exceção de domínio que serve.
- **Autorização** vem de `app/api/deps.py`: `obter_usuario_atual`, `require_gestor`, `require_perfis(...)`. A identidade (quem é o aluno/gestor) **deriva do token**, nunca do corpo da requisição.

## Coordenação entre instâncias (anti-colisão)
Duas instâncias editando o mesmo arquivo em paralelo = uma sobrescreve a outra no merge. Particionem o trabalho por **fatia de domínio**, não por achado.

Como a arquitetura é **por camada** (e uma feature atravessa router + service + repository), o seam natural aqui é o **grupo de domínio**: `provas`, `simulados`, `respostas`, `questoes`, `etiquetas`, `importacao`, `auth`, `turmas`. Cada dev pega um grupo diferente e toca o router + service + repository daquela fatia.

Antes de começar:
1. Combine com o outro operador qual fatia é de cada um. Evitem fatias que se cruzam.
2. Cuidado redobrado com **arquivos transversais** — `models.py`, `enums.py`, `config.py`, `database.py`, `main.py`, `deps.py` e migrações Alembic: mudança ali aparece no PR do outro. Coordene **antes**.
3. Se precisar tocar um arquivo que o outro já está mexendo: **espere, pegue outra fatia, ou peça ao operador para coordenar a ordem.** Não edite em paralelo.

(Se adotarem `EDITING.md`, declare ali os arquivos que vai tocar antes de começar e remova a linha ao terminar.)

## Git workflow
O paralelismo só funciona com sync disciplinado. Trabalhar sobre código velho é conflito garantido.

- Branch própria por tarefa: `tipo/escopo-curto` (ex.: `feat/relatorio-turma`, `fix/gabarito-6-alternativas`). **Nunca commite direto na `main`.**
- ANTES de começar: `git switch main && git pull` e crie a branch a partir da main fresca.
- ANTES de abrir o PR: puxe a main de novo e integre (`git pull --rebase origin main`). Resolva conflito na **sua** branch, nunca na main.
- Branch curta no tempo. Abra PR cedo, mesmo parcial, e sinalize.
- Conflito em arquivo transversal ou config compartilhada: **PARE e confirme** com o operador antes de decidir qual versão fica.
- Nunca force-push em branch compartilhada (em branch própria não revisada, tudo bem).

> **Estado atual do portão (importante):** **ainda NÃO há CI** (`.github/workflows/` não existe) e a branch `main` **não está protegida** no GitHub. Hoje a disciplina é **manual** — o portão de qualidade é você rodar localmente antes do PR. **Recomendação forte com 2 devs:** configurar GitHub Actions rodando `pytest` + proteção de branch (PR obrigatório para entrar na `main`). Enquanto isso não existir, redobre o cuidado.

## Portão de qualidade (hoje local)
Antes de marcar a tarefa como pronta / abrir o PR, rode localmente e **relate o resultado** ao operador:
1. `pytest` — **tem que estar 100% verde.** Não delegue ao "depois".
2. `alembic upgrade head` — aplica limpo. Se mexeu em `models.py`, gere a migração (`alembic revision --autogenerate -m "..."`) e **revise o arquivo gerado** antes de commitar.
3. A app sobe: `uvicorn app.api.main:app --reload` responde em `/health` e `/docs`.

Se o seu PR quebrou algo que estava verde, é sua responsabilidade consertar antes do merge.

## Stack e comandos
```bash
# Ambiente (cada dev tem o seu — .venv NÃO é versionado nem portável entre máquinas)
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # PowerShell  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt

alembic upgrade head                  # cria/atualiza o schema
uvicorn app.api.main:app --reload     # sobe a API  → /docs (Swagger), / (página demo)
pytest                                # testes
docker build -t seduc-simulados . && docker run -p 8000:8000 --env-file .env seduc-simulados
```
Seeds de demonstração (opcional): `scripts/seed_etiquetas.py`, `seed_demo.py`, `seed_questoes_demo.py`, `seed_questoes_extra.py`. Usuários demo (senha `sedu123`): `admin@`, `gestor@`, `aluno@sedu.se.gov.br`.

## Convenções de código (Python / FastAPI)
- **Identificadores em português** (`obter_usuario_atual`, `prova_service`, `montar_questoes`, `buscar_por_email`) — é o padrão do repo. Mantenha. Classes em `PascalCase`; funções, variáveis e módulos em `snake_case`.
- **Type hints sempre**, no estilo moderno (`str | None`, `list[str]`, `Annotated`). Use `from __future__ import annotations` no topo quando ajudar.
- **Config por ambiente** via `app/config.py` (pydantic-settings, prefixo `SEDU_`). Não leia `os.environ` espalhado — adicione o campo em `Settings`.
- **Erros** pelas exceções de domínio de `app/exceptions.py` (ver seção de arquitetura).
- **Mensagens ao usuário em português** (erros, descrições do Swagger).
- Comentário só onde agrega; siga a densidade do arquivo vizinho.

## Contrato da API — cuidado especial
O `REVIEW.md` (ARCH-5) registra que **o front oficial e este backend foram desenhados contra contratos incompatíveis** (tipo de `id`, vocabulário código vs. label PT, envelope `{dados, meta}`, prefixo `/api`, token em header vs. cookie). Hoje o front roda em mocks, então nada quebra — mas **qualquer mudança na superfície da API** (rotas, formato de request/response, nomes de campos, status codes) pode quebrar a integração futura.

→ Não altere o contrato de fio unilateralmente. Mudou rota ou shape de resposta? **Sinalize ao operador** para alinhar com o front antes.

## Onde você pode atuar livremente
- Dentro da **fatia de domínio** designada na tarefa atual (seu router + service + repository).
- Lógica interna, helpers e testes daquela fatia.
- Refatorações locais que não vazam a interface pública do módulo nem o contrato da API.

## Quando você DEVE parar e pedir confirmação
Não execute, pergunte primeiro, antes de:
- Alterar **schema/migrações** (`models.py`, Alembic) ou qualquer contrato de dados.
- Mexer em **config compartilhada**: `config.py`, variáveis `SEDU_*`, `requirements*.txt`, `Dockerfile`, `alembic.ini`.
- Mudar a **superfície da API** (rotas, request/response, status) — ver "Contrato da API".
- Mexer em **autenticação/autorização** (`deps.py`, `auth_service.py`, regras de perfil).
- Tocar **arquivos transversais** (`main.py`, `enums.py`, `database.py`) ou a interface pública de um módulo.
- Tocar a fatia de domínio de outra instância, mesmo para "uma correção rápida".
- Adicionar, remover ou atualizar **dependências**.
- Renomear, mover ou deletar arquivos existentes.
- Introduzir um padrão arquitetural que quebra a regra de camadas.

**Regra prática:** se a mudança pode aparecer no PR do outro dev, pergunte antes.

## Estilo de código
Não imponha seu estilo. Inspecione o código vizinho e siga o que já existe: nomenclatura, tratamento de erro (exceções de domínio), densidade de comentário, granularidade de função/arquivo. Em caso de inconsistência interna, siga o padrão do módulo onde a tarefa está acontecendo.

## Granularidade de trabalho
- Uma tarefa = uma mudança coerente. Não junte refatoração + feature + fix.
- Se a tarefa cresceu além do combinado durante a execução, **pare e relate** antes de continuar.
- Prefira PRs pequenos. Passou de ~300 linhas alteradas, sinalize ao operador.

## Commits e PRs
- Formato: `tipo(escopo): descrição` (ex.: `feat(relatorio): agrega notas por turma`). Um commit = uma mudança lógica.
- **Não** adicione `Co-Authored-By: Claude` nem "Generated with Claude Code" nas mensagens.
- Mensagem multi-linha: use `git commit -F <arquivo>` (evita problema de escaping no shell).
- Antes de finalizar, rode o portão local (`pytest`) e relate o resultado.
- Ao final, resuma em uma frase o que mudou e onde, para a descrição do PR.

## Segredos e configuração
- **Nunca** commite `.env`, `SEDU_JWT_SECRET`, bancos `*.db`/`*.sqlite`. Já estão no `.gitignore`.
- Documente toda variável nova em `.env.example` (sem valor real).
- Em produção (`SEDU_AMBIENTE=producao`), `app/config.py` **falha rápido** se o segredo for fraco/ausente — não burle isso com fallback.

## O que NÃO fazer
- Não decida arquitetura sozinho. Proponha, espere confirmação.
- Não otimize/refatore código alheio sem pedido explícito.
- Não adicione "melhorias" fora do escopo do PR atual — anote como tarefa futura.
- Não reabra achado do `REVIEW.md` que já foi corrigido — confira o código atual antes.
- Não troque biblioteca "porque seria melhor" se o projeto já fez uma escolha equivalente.
- Não quebre a regra de camadas por conveniência (router falando ORM, router commitando).

## Quando travado entre opções razoáveis
Apresente as opções ao operador com prós e contras curtos. Não decida no escuro. O custo de uma pergunta é baixo; o de duas instâncias tomando decisões arquiteturais incompatíveis em paralelo é alto.

## Sinalizações obrigatórias ao operador
- "Isto muda a superfície da API — confirmar com o front antes de seguir?"
- "Preciso mexer em `models.py`/migração — confirmo o schema?"
- "Esta tarefa cruza a fatia de domínio do outro dev — como coordenar?"
- "Isto toca autenticação/autorização — quero confirmação."
- "Isto adiciona dependência nova — confirmar?"
- "Puxei a main e deu conflito em arquivo transversal/config — não vou resolver no escuro."
- "Achei o `REVIEW.md` divergente do código atual — qual é a verdade?"
