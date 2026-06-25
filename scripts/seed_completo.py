"""Seed COMPLETO para testes — um cenário realista que exercita tudo, inclusive a IA.

Cria: 1 escola, 3 turmas do 9º ano, ~30 alunos com PERFIS variados (do excelente ao
evadindo), um banco rico de Matemática (6 conteúdos, alguns propositalmente difíceis) e
simulados em todos os estados. Os simulados FINALIZADOS recebem respostas calibradas pela
habilidade de cada aluno e pela dificuldade de cada conteúdo — assim:

- GET /ia/risco/{aluno_id} mostra risco baixo (engajados) a alto (evadindo);
- GET /ia/diagnostico/{simulado_id} encontra conteúdos fracos reais (Equações, Geometria);
- o ciclo do simulado (liberado/gerado/rascunho) tem exemplos em cada fase.

A IA é DESLIGADA durante o seed (geração clássica, rápida e determinística — sem custo de
API). Os endpoints de IA você testa depois, com a chave, sobre os dados aqui criados.

Como rodar (com o banco já migrado: alembic upgrade head):
    python scripts/seed_completo.py
Reexecutar é seguro: questões/usuários não duplicam e os simulados são pulados se já existirem.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select  # noqa: E402

# Desliga a curadoria por IA ANTES de importar o que usa o serviço: o seed gera no modo
# clássico (sem chamar a Claude) — rápido, grátis e reproduzível.
from app.config import settings  # noqa: E402

settings.ia_curadoria_habilitada = False

from app.database import SessionLocal  # noqa: E402
from app.enums import PerfilUsuario, StatusSimulado  # noqa: E402
from app.models import (  # noqa: E402
    Aluno,
    Alternativa,
    Conteudo,
    Escola,
    Materia,
    Nivel,
    Questao,
    Resposta,
    Serie,
    Simulado,
    Turma,
    Usuario,
)
from app.services import auth_service, simulado_service  # noqa: E402

SENHA = "sedu123"
SERIE = "9º ano"
SEED = 2026  # tudo determinístico

# --- Banco de Matemática: (conteudo, nivel, enunciado, [(alt, correta), ...]) ---
QUESTOES_MAT = [
    # Operações
    ("Operações", "Fácil", "Quanto é 7 × 8?",
     [("56", True), ("54", False), ("63", False), ("48", False)]),
    ("Operações", "Fácil", "Qual o resultado de 144 ÷ 12?",
     [("12", True), ("10", False), ("14", False), ("11", False)]),
    ("Operações", "Médio", "Quanto é (-5) + 12 - 3?",
     [("4", True), ("-4", False), ("10", False), ("2", False)]),
    ("Operações", "Médio", "Calcule 2³ + 3².",
     [("17", True), ("12", False), ("15", False), ("13", False)]),
    ("Operações", "Difícil", "Quanto é √81 + √64?",
     [("17", True), ("15", False), ("13", False), ("145", False)]),
    # Frações
    ("Frações", "Fácil", "Quanto é 1/2 + 1/4?",
     [("3/4", True), ("2/6", False), ("1/6", False), ("2/4", False)]),
    ("Frações", "Fácil", "Simplifique a fração 6/8.",
     [("3/4", True), ("2/4", False), ("6/4", False), ("1/2", False)]),
    ("Frações", "Médio", "Quanto é 2/3 × 3/4?",
     [("1/2", True), ("6/7", False), ("5/12", False), ("2/4", False)]),
    ("Frações", "Médio", "Quanto é 3/5 de 100?",
     [("60", True), ("35", False), ("53", False), ("15", False)]),
    ("Frações", "Difícil", "Quanto é (1/2) ÷ (1/4)?",
     [("2", True), ("1/8", False), ("1/2", False), ("8", False)]),
    # Porcentagem
    ("Porcentagem", "Fácil", "Quanto é 10% de 200?",
     [("20", True), ("10", False), ("2", False), ("100", False)]),
    ("Porcentagem", "Fácil", "50% equivale a qual fração?",
     [("1/2", True), ("1/4", False), ("1/5", False), ("2/1", False)]),
    ("Porcentagem", "Médio", "Um produto de R$ 80 com 25% de desconto passa a custar:",
     [("R$ 60", True), ("R$ 55", False), ("R$ 20", False), ("R$ 75", False)]),
    ("Porcentagem", "Médio", "Numa turma de 40 alunos, 30% faltaram. Quantos faltaram?",
     [("12", True), ("10", False), ("30", False), ("14", False)]),
    ("Porcentagem", "Difícil", "Um valor subiu de 200 para 250. Qual foi o aumento percentual?",
     [("25%", True), ("50%", False), ("20%", False), ("30%", False)]),
    # Equações do 1º grau (conteúdo difícil de propósito)
    ("Equações do 1º grau", "Fácil", "Resolva: x + 5 = 12.",
     [("x = 7", True), ("x = 17", False), ("x = 5", False), ("x = 60", False)]),
    ("Equações do 1º grau", "Fácil", "Resolva: 2x = 10.",
     [("x = 5", True), ("x = 20", False), ("x = 8", False), ("x = 12", False)]),
    ("Equações do 1º grau", "Médio", "Resolva: 3x - 4 = 11.",
     [("x = 5", True), ("x = 7", False), ("x = 3", False), ("x = 15", False)]),
    ("Equações do 1º grau", "Médio", "Resolva: 2x + 3 = x + 9.",
     [("x = 6", True), ("x = 3", False), ("x = 12", False), ("x = 4", False)]),
    ("Equações do 1º grau", "Difícil", "Resolva: 5(x - 2) = 3x + 4.",
     [("x = 7", True), ("x = 3", False), ("x = 1", False), ("x = 14", False)]),
    # Geometria (conteúdo difícil de propósito)
    ("Geometria", "Fácil", "Quantos lados tem um hexágono?",
     [("6", True), ("5", False), ("7", False), ("8", False)]),
    ("Geometria", "Fácil", "A soma dos ângulos internos de um triângulo é:",
     [("180°", True), ("360°", False), ("90°", False), ("270°", False)]),
    ("Geometria", "Médio", "A área de um quadrado de lado 5 cm é:",
     [("25 cm²", True), ("20 cm²", False), ("10 cm²", False), ("50 cm²", False)]),
    ("Geometria", "Médio", "O perímetro de um retângulo de lados 4 cm e 6 cm é:",
     [("20 cm", True), ("24 cm", False), ("10 cm", False), ("48 cm", False)]),
    ("Geometria", "Difícil", "Num triângulo retângulo de catetos 3 e 4, a hipotenusa mede:",
     [("5", True), ("7", False), ("6", False), ("25", False)]),
    # Estatística
    ("Estatística", "Fácil", "A média aritmética de 4, 6 e 8 é:",
     [("6", True), ("18", False), ("5", False), ("7", False)]),
    ("Estatística", "Fácil", "Qual é a moda do conjunto {2, 3, 3, 5, 7}?",
     [("3", True), ("5", False), ("2", False), ("7", False)]),
    ("Estatística", "Médio", "A mediana do conjunto {1, 3, 5, 7, 9} é:",
     [("5", True), ("3", False), ("7", False), ("4", False)]),
    ("Estatística", "Médio", "A média de 10, 20 e 30 é:",
     [("20", True), ("30", False), ("15", False), ("60", False)]),
    ("Estatística", "Difícil", "A média de 5 notas é 7. Se a soma de 4 delas é 26, a 5ª nota é:",
     [("9", True), ("7", False), ("8", False), ("5", False)]),
]

# Conteúdos mais difíceis recebem facilidade < 1 (geram mais erro -> viram ponto fraco).
FACILIDADE_CONTEUDO = {
    "Operações": 1.05,
    "Estatística": 0.95,
    "Porcentagem": 0.9,
    "Frações": 0.8,
    "Geometria": 0.65,
    "Equações do 1º grau": 0.55,
}
FACILIDADE_NIVEL = {"Fácil": 1.15, "Médio": 0.95, "Difícil": 0.7}

# Perfis de aluno: (rótulo, habilidade base, participação). Determinam risco/desempenho.
PERFIS = [
    ("excelente", 0.92, 1.00),
    ("muito bom", 0.82, 0.95),
    ("bom", 0.72, 0.90),
    ("mediano", 0.60, 0.80),
    ("com dificuldade", 0.48, 0.70),
    ("em risco", 0.40, 0.40),
    ("evadindo", 0.33, 0.15),
]

NOMES = [
    "Ana Beatriz Souza", "Bruno Carvalho Lima", "Carla Mendes Rocha", "Diego Santos Alves",
    "Eduarda Nunes Pires", "Felipe Oliveira Cruz", "Gabriela Ramos Dias", "Heitor Costa Melo",
    "Isabela Freitas Gomes", "João Pedro Barbosa", "Kauã Ribeiro Teles", "Larissa Vieira Cunha",
    "Matheus Andrade Reis", "Natália Cardoso Pinto", "Otávio Moreira Lopes", "Priscila Tavares Sá",
    "Rafael Monteiro Luz", "Sophia Almeida Faria", "Thiago Borges Nunes", "Valentina Cruz Rios",
    "William Farias Pena", "Yasmin Lopes Dantas", "Arthur Mota Viana", "Beatriz Nogueira Sales",
    "Caio Henrique Brito", "Daniela Aragão Melo", "Enzo Gabriel Pires", "Fernanda Quintela Sá",
    "Gustavo Caldas Lira", "Helena Marques Brito",
]


def _obter_ou_criar(sessao, modelo, **filtros):
    inst = sessao.scalar(select(modelo).filter_by(**filtros))
    if inst is None:
        inst = modelo(**filtros)
        sessao.add(inst)
        sessao.flush()
    return inst


def _semear_etiquetas(sessao):
    for nome in (SERIE,):
        _obter_ou_criar(sessao, Serie, nome=nome)
    for nome in ("Fácil", "Médio", "Difícil"):
        _obter_ou_criar(sessao, Nivel, nome=nome)
    sessao.flush()


def _semear_questoes(sessao):
    serie = sessao.scalar(select(Serie).where(Serie.nome == SERIE))
    niveis = {n.nome: n for n in sessao.scalars(select(Nivel))}
    materia = _obter_ou_criar(sessao, Materia, nome="Matemática")
    criadas = 0
    for conteudo_nome, nivel_nome, enunciado, alts in QUESTOES_MAT:
        if sessao.scalar(select(Questao).where(Questao.enunciado == enunciado)):
            continue
        conteudo = _obter_ou_criar(
            sessao, Conteudo, nome=conteudo_nome, materia_id=materia.id
        )
        sessao.add(
            Questao(
                enunciado=enunciado,
                serie=serie,
                materia=materia,
                conteudo=conteudo,
                nivel=niveis[nivel_nome],
                adaptacoes=[],
                alternativas=[
                    Alternativa(texto=t, correta=c, ordem_original=i)
                    for i, (t, c) in enumerate(alts, start=1)
                ],
            )
        )
        criadas += 1
    sessao.flush()
    return criadas


def _semear_usuarios_e_turmas(sessao, rng):
    """Cria os usuários demo + gestor/admin/suporte + 3 turmas com ~30 alunos perfilados."""
    serie = sessao.scalar(select(Serie).where(Serie.nome == SERIE))
    escola = _obter_ou_criar(
        sessao, Escola, nome="Escola Estadual Modelo", municipio="Aracaju"
    )

    def cria_usuario(nome, email, perfil):
        u = sessao.scalar(select(Usuario).where(Usuario.email == email))
        if u is None:
            u = Usuario(
                nome=nome,
                email=email,
                senha_hash=auth_service.gerar_hash_senha(SENHA),
                perfil=perfil,
            )
            sessao.add(u)
            sessao.flush()
        return u

    # Usuários demo (mantém o login conhecido) + equipe gestora.
    cria_usuario("Administrador SEDU", "admin@sedu.se.gov.br", PerfilUsuario.ADMIN)
    gestor = cria_usuario("Maria Gestora", "gestor@sedu.se.gov.br", PerfilUsuario.GESTOR)
    cria_usuario("Suporte Pedagógico", "suporte@sedu.se.gov.br", PerfilUsuario.SUPORTE)

    turmas = []
    for letra in ("9A", "9B", "9C"):
        turma = _obter_ou_criar(
            sessao,
            Turma,
            escola_id=escola.id,
            serie_id=serie.id,
            nome=letra,
            ano_letivo=2026,
        )
        turmas.append(turma)
    sessao.flush()

    # ~30 alunos distribuídos pelas turmas, cada um com um perfil (habilidade/participação).
    alunos = []  # (Aluno, habilidade, participacao, rotulo)
    # O 1º aluno reusa o login demo aluno@ para continuar funcionando.
    plano = []
    for i, nome in enumerate(NOMES):
        rotulo, hab, part = PERFIS[i % len(PERFIS)]
        # leve variação individual para não ficar tudo igual
        hab = max(0.2, min(0.97, hab + rng.uniform(-0.05, 0.05)))
        email = "aluno@sedu.se.gov.br" if i == 0 else (
            f"aluno{i+1:02d}@sedu.se.gov.br"
        )
        plano.append((nome, email, rotulo, hab, part))

    for idx, (nome, email, rotulo, hab, part) in enumerate(plano):
        turma = turmas[idx % len(turmas)]
        usuario = cria_usuario(nome, email, PerfilUsuario.ALUNO)
        aluno = sessao.scalar(select(Aluno).where(Aluno.usuario_id == usuario.id))
        if aluno is None:
            aluno = Aluno(usuario=usuario, turma=turma, perfil_cognitivo=[rotulo])
            sessao.add(aluno)
            sessao.flush()
        alunos.append((aluno, hab, part, rotulo, turma.id))
    sessao.flush()
    return gestor, turmas, alunos


def _prob_acerto(habilidade, conteudo, nivel):
    p = habilidade * FACILIDADE_CONTEUDO.get(conteudo, 1.0) * FACILIDADE_NIVEL.get(nivel, 1.0)
    return max(0.03, min(0.97, p))


def _responder(sessao, simulado_id, alunos_turma, rng, *, completo):
    """Cria respostas calibradas. completo=True: todos que participam respondem tudo
    (simulado a finalizar). completo=False: participação parcial (simulado liberado)."""
    questoes = simulado_service.montar_questoes(
        sessao, simulado_id=simulado_id, incluir_gabarito=True
    )
    for aluno, hab, part, _rotulo, _turma in alunos_turma:
        if rng.random() > part:  # aluno não engajou neste simulado
            continue
        for q in questoes:
            # No liberado (em andamento), alguns largam no meio.
            if not completo and rng.random() > 0.7:
                continue
            p = _prob_acerto(hab, q["conteudo"], q["nivel"])
            acertou = rng.random() < p
            if acertou:
                alt_id = next(a["alternativa_id"] for a in q["alternativas"] if a["correta"])
            else:
                erradas = [a["alternativa_id"] for a in q["alternativas"] if not a["correta"]]
                alt_id = rng.choice(erradas)
            sessao.add(
                Resposta(
                    aluno_id=aluno.id,
                    simulado_id=simulado_id,
                    questao_id=q["questao_id"],
                    alternativa_id=alt_id,
                    correta=acertou,
                )
            )
    sessao.flush()


def _criar_simulado(sessao, gestor_id, turma_id, titulo, *, quantidade, seed):
    parametros = {
        "serie": SERIE,
        "materia": "Matemática",
        "distribuicao": {"Fácil": 0.4, "Médio": 0.4, "Difícil": 0.2},
        "quantidade": quantidade,
        "seed": seed,
    }
    sim = simulado_service.criar_simulado(
        sessao,
        gestor_id=gestor_id,
        turma_id=turma_id,
        titulo=titulo,
        parametros=parametros,
    )
    return sim


def _semear_simulados(sessao, gestor, turmas, alunos, rng):
    """Por turma: 2 finalizados (com respostas) + 1 liberado + 1 gerado + 1 rascunho."""
    if sessao.scalar(select(Simulado).limit(1)) is not None:
        return 0  # já há simulados: não duplica

    criados = 0
    seed_base = SEED
    for ti, turma in enumerate(turmas):
        alunos_turma = [a for a in alunos if a[4] == turma.id]

        # 2 finalizados (history para risco + diagnóstico)
        for k in range(1, 3):
            sim = _criar_simulado(
                sessao, gestor.id, turma.id,
                f"Simulado Matemática {turma.nome} — Diagnóstico {k}",
                quantidade=10, seed=seed_base + ti * 10 + k,
            )
            simulado_service.gerar_e_persistir(sessao, simulado_id=sim.id, seed=sim.id)
            simulado_service.liberar(sessao, simulado_id=sim.id)
            _responder(sessao, sim.id, alunos_turma, rng, completo=True)
            simulado_service.finalizar_e_corrigir(sessao, simulado_id=sim.id)
            criados += 1

        # 1 liberado (em andamento, respostas parciais)
        sim = _criar_simulado(
            sessao, gestor.id, turma.id,
            f"Simulado Matemática {turma.nome} — Em andamento",
            quantidade=8, seed=seed_base + ti * 10 + 5,
        )
        simulado_service.gerar_e_persistir(sessao, simulado_id=sim.id, seed=sim.id)
        simulado_service.liberar(sessao, simulado_id=sim.id)
        _responder(sessao, sim.id, alunos_turma, rng, completo=False)
        criados += 1

        # 1 gerado (pronto para liberar)
        sim = _criar_simulado(
            sessao, gestor.id, turma.id,
            f"Simulado Matemática {turma.nome} — Pronto",
            quantidade=8, seed=seed_base + ti * 10 + 6,
        )
        simulado_service.gerar_e_persistir(sessao, simulado_id=sim.id, seed=sim.id)
        criados += 1

        # 1 rascunho
        _criar_simulado(
            sessao, gestor.id, turma.id,
            f"Simulado Matemática {turma.nome} — Rascunho",
            quantidade=8, seed=seed_base + ti * 10 + 7,
        )
        criados += 1

    return criados


def main() -> None:
    rng = random.Random(SEED)
    with SessionLocal() as sessao:
        _semear_etiquetas(sessao)
        novas_q = _semear_questoes(sessao)
        gestor, turmas, alunos = _semear_usuarios_e_turmas(sessao, rng)
        sessao.commit()
        novos_sim = _semear_simulados(sessao, gestor, turmas, alunos, rng)
        sessao.commit()

        # --- Resumo ---
        total_q = sessao.scalar(select(func.count(Questao.id)))
        total_alunos = sessao.scalar(select(func.count(Aluno.id)))
        finalizados = sessao.scalars(
            select(Simulado).where(Simulado.status == StatusSimulado.FINALIZADO)
        ).all()

        print("=" * 64)
        print(" BANCO DE TESTES COMPLETO PRONTO")
        print("=" * 64)
        print(f"Questões de Matemática: {total_q}  (+{novas_q} criadas agora)")
        print(f"Turmas: {', '.join(t.nome for t in turmas)} | Alunos: {total_alunos}")
        print(f"Simulados criados: {novos_sim}  (2 finalizados + liberado + gerado + rascunho por turma)")
        print()
        print(f"Login (senha de todos: {SENHA}):")
        print("  admin@sedu.se.gov.br | gestor@sedu.se.gov.br | suporte@sedu.se.gov.br")
        print("  aluno@sedu.se.gov.br + aluno02@.. aluno30@.. (perfis variados)")
        print()
        print("Para testar a IA (GET, precisa de token de gestor):")
        # Mostra um aluno de cada extremo de perfil para risco.
        por_rotulo = {}
        for aluno, hab, part, rotulo, _t in alunos:
            por_rotulo.setdefault(rotulo, aluno.id)
        baixo = por_rotulo.get("excelente")
        alto = por_rotulo.get("evadindo")
        print(f"  Risco esperado BAIXO:  GET /ia/risco/{baixo}   (aluno 'excelente')")
        print(f"  Risco esperado ALTO:   GET /ia/risco/{alto}   (aluno 'evadindo')")
        if finalizados:
            print(f"  Diagnóstico da turma:  GET /ia/diagnostico/{finalizados[0].id}   (simulado finalizado)")
        print()
        print("Dica: a IA de verdade (curadoria/diagnóstico) usa a Claude quando")
        print("SEDU_IA_CURADORIA_HABILITADA=true + chave no .env. A predição (sklearn) sempre roda.")


if __name__ == "__main__":
    main()
