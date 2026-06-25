# Plano de trabalho em equipe — Backend SEDUC Simulados

Divisão do trabalho restante (segundo o Backlog v4) em **duas frentes paralelas** que tocam **arquivos diferentes**, para evitar conflitos. Repositório canônico: `AltemirFilho/projeto_Seduc`.

## ⚠️ Regras de git (obrigatórias — leia antes de começar)

Aconteceu um incidente em que uma sincronização apagou o trabalho de outra pessoa. Para nunca mais:

1. **Antes de começar:** `git checkout main && git pull origin main`.
2. **Trabalhe SEMPRE numa branch própria** (nunca direto na `main`):
   - Frente A: `git checkout -b feat/relatorios-gestao`
   - Frente B: `git checkout -b feat/ia-infra`
3. **Suba a sua branch** (`git push -u origin <sua-branch>`) e **abra um Pull Request**. A `main` só recebe código via PR, depois que o outro der uma olhada.
4. **NUNCA** use `git push --force`, `rm -rf` em pastas que você não criou, nem apague arquivos da frente do outro.
5. Cada um mexe **só nos arquivos da sua frente** (lista abaixo). Os 3 arquivos compartilhados (`main.py`, `models.py`, `requirements.txt`) são **append-only**: só adicione, nunca reescreva o bloco do outro.

## Convenções do projeto (as duas frentes seguem)

- **Camadas:** router (`app/api/routers/`) → service (`app/services/`) → repository (`app/repositories/`) → models. Router não monta query; service tem a regra; repository fala com o banco.
- **Erros:** levante exceções de domínio de `app/exceptions.py` (`NaoEncontrado`, `RegraNegocio`, `DadosInvalidos`, `PermissaoNegada`). Não use `HTTPException` nos services; o handler central converte.
- **Autorização:** use as dependências de `app/api/deps.py` — `Depends(require_gestor)` para gestor/admin, `Depends(obter_usuario_atual)` para qualquer autenticado. Identidade do usuário vem do token, nunca do corpo.
- **Config:** nada hardcoded; use `app/config.py` (`settings`).
- **Testes:** todo endpoint novo ganha teste em `tests/` (siga o `conftest.py`). Rode `pytest` antes de abrir o PR.
- **Migração:** mudou `models.py`? Gere `alembic revision --autogenerate -m "..."` e confira o arquivo gerado (o autogen às vezes esquece o import de `Text`).

---

## FRENTE A — Resultados, Relatórios e Gestão (sem IA)

**Responsável:** Sócio · **Branch:** `feat/relatorios-gestao`

**Entregas (Backlog Épicos 2, 3, 6):**
1. `GET /relatorios/turma/{turma_id}` — média da turma, ranking de conteúdos por taxa de erro, nº de alunos. Derivado da tabela `respostas` (sem IA).
2. `GET /simulados/{id}/meu-resultado` — o aluno autenticado vê sua nota, quais questões errou e o gabarito.
3. Exportar relatório da turma em **PDF/CSV**.
4. `POST /usuarios` e `GET /usuarios` — admin/gestor cadastra e lista alunos vinculados a uma turma (Épico 2).
5. `PATCH /questoes/{id}` e `GET /questoes/{id}` — editar e ver uma questão (Épico 3).

**Arquivos seus (crie/edite só estes):**
- Novos: `app/api/routers/relatorios.py`, `app/api/routers/usuarios.py`, `app/services/relatorio_service.py`, `app/services/usuario_service.py`, `app/repositories/resposta_repository.py`
- Edita: `app/api/routers/questoes.py`, `app/services/questao_service.py`
- Testes: `tests/test_relatorios.py`, `tests/test_usuarios.py`, `tests/test_questoes_edicao.py`
- **NÃO toque em:** `app/services/simulado_service.py`, `app/models.py`, `app/integrations/`.

---

## FRENTE B — Inteligência Artificial e Infraestrutura

**Responsável:** Altemir · **Branch:** `feat/ia-infra`

**Entregas (Backlog Épicos 4, 7 + infra):**
1. **Curadoria por IA (Claude API)** — `app/integrations/claude.py` + `app/services/ia_curadoria_service.py`. O `gerar_e_persistir` do simulado passa a chamar a IA para balancear/ordenar; com **fallback para a seleção clássica** (`prova_service`) em caso de timeout/baixa confiança (marca flag). Resiliência: timeout + retry.
2. **Predição de risco de evasão (scikit-learn)** — `app/services/predicao_service.py` + `app/integrations/ml_service.py`. Endpoint `GET /ia/risco/{aluno_id}`.
3. **Diagnóstico pedagógico por IA** — `GET /ia/diagnostico/{simulado_id}` (resumo da turma via Claude).
4. **Novos modelos:** `predicao_risco` e `diagnostico_turma` (adicione ao FINAL de `app/models.py`) + migração Alembic.
5. **Infra (opcional, atrás de config):** driver PostgreSQL (`psycopg`) e Redis (fila para reprocessar curadoria).

**Arquivos seus (crie/edite só estes):**
- Novos: `app/integrations/claude.py`, `app/integrations/ml_service.py`, `app/services/ia_curadoria_service.py`, `app/services/predicao_service.py`, `app/services/diagnostico_service.py`, `app/api/routers/ia.py`
- Edita: `app/services/simulado_service.py` (só `gerar_e_persistir`), `app/models.py` (adiciona 2 tabelas no fim)
- Testes: `tests/test_ia.py`
- **NÃO toque em:** `app/api/routers/questoes.py`, `app/services/questao_service.py`, `relatorio_service.py`, `usuario_service.py`.

---

## Arquivos compartilhados (cuidado redobrado)

| Arquivo | Frente A adiciona | Frente B adiciona |
|---|---|---|
| `app/api/main.py` | `include_router(relatorios)`, `include_router(usuarios)` | `include_router(ia)` |
| `app/models.py` | — | tabelas `predicao_risco`, `diagnostico_turma` (no fim) |
| `requirements.txt` | (talvez `reportlab` p/ PDF) | `anthropic`, `scikit-learn`, `redis`, `psycopg[binary]` |

Como ambos mexem no `main.py`, combinem de mergear um PR de cada vez (o segundo resolve o conflitinho de import).

## Como rodar (as duas frentes)

```
pip install -r requirements-dev.txt
alembic upgrade head
python scripts/seed_etiquetas.py ; python scripts/seed_demo.py ; python scripts/seed_questoes_demo.py
pytest
uvicorn app.api.main:app --reload   # http://127.0.0.1:8000/docs
```
