from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.exceptions import DadosInvalidos, RegraNegocio
from app.models import Questao
from app.repositories import etiqueta_repository, questao_repository

LETRAS = "ABCDE"
MAX_ALTERNATIVAS = len(LETRAS)


@dataclass
class AlternativaProva:
    letra: str
    texto: str
    alternativa_id: int


@dataclass
class QuestaoProva:
    ordem: int
    questao_id: int
    enunciado: str
    materia: str
    conteudo: str
    nivel: str
    alternativas: list[AlternativaProva]
    gabarito: str


@dataclass
class Prova:
    serie: str
    materias: list[str]
    total: int
    distribuicao_real: dict[str, int]
    questoes: list[QuestaoProva] = field(default_factory=list)

    def gabarito_dict(self) -> dict[int, str]:
        return {q.ordem: q.gabarito for q in self.questoes}


def _validar_distribuicao(distribuicao: dict[str, float]) -> None:
    if not isinstance(distribuicao, dict) or not distribuicao:
        raise DadosInvalidos("distribuição inválida")
    for nivel, proporcao in distribuicao.items():
        # bool é subclasse de int: barramos explicitamente. math.isfinite descarta NaN e
        # infinito, que passariam batido pela checagem de soma (NaN != NaN) e estourariam
        # depois em round(NaN) — virando um 500 em vez de um 422 claro.
        if (
            isinstance(proporcao, bool)
            or not isinstance(proporcao, (int, float))
            or not math.isfinite(proporcao)
            or proporcao < 0
        ):
            raise DadosInvalidos(f"proporção inválida para o nível '{nivel}'")
    soma = sum(distribuicao.values())
    if abs(soma - 1.0) > 0.01:
        raise DadosInvalidos(
            f"as proporções da distribuição devem somar 1.0 (somaram {soma:.2f})"
        )


def _selecionar_por_distribuicao(
    candidatas: list[Questao],
    distribuicao: dict[str, float],
    quantidade: int,
    rng: random.Random,
) -> list[Questao]:
    por_nivel: dict[str, list[Questao]] = {}
    for q in candidatas:
        por_nivel.setdefault(q.nivel.nome, []).append(q)
    for lista in por_nivel.values():
        rng.shuffle(lista)

    selecionadas: list[Questao] = []
    for nivel_nome, proporcao in distribuicao.items():
        alvo = round(quantidade * proporcao)
        disponiveis = por_nivel.get(nivel_nome, [])
        selecionadas.extend(disponiveis[:alvo])

    if len(selecionadas) < quantidade:
        ja_escolhidas = {id(q) for q in selecionadas}
        resto = [q for q in candidatas if id(q) not in ja_escolhidas]
        rng.shuffle(resto)
        selecionadas.extend(resto[: quantidade - len(selecionadas)])

    rng.shuffle(selecionadas)
    return selecionadas[:quantidade]


def gerar_prova(
    sessao: Session,
    *,
    serie: str,
    materia: Optional[str] = None,
    materias: Optional[Sequence[str]] = None,
    conteudos: Optional[Sequence[str]] = None,
    distribuicao: Optional[dict[str, float]] = None,
    quantidade: int = 10,
    adaptacoes: Optional[Sequence[str]] = None,
    seed: Optional[int] = None,
    selecao_ids: Optional[Sequence[int]] = None,
) -> Prova:
    if quantidade < 1:
        raise DadosInvalidos("a quantidade de questões deve ser pelo menos 1")
    if distribuicao:
        _validar_distribuicao(distribuicao)
        # As chaves precisam casar EXATAMENTE com os níveis do banco. Sem isto, um typo
        # como 'Facil' (sem acento) era ignorado em silêncio e a prova saía aleatória,
        # parecendo balanceada.
        niveis_validos = {n.nome for n in etiqueta_repository.listar_niveis(sessao)}
        desconhecidos = sorted(k for k in distribuicao if k not in niveis_validos)
        if desconhecidos:
            raise DadosInvalidos(
                "nível(is) desconhecido(s) na distribuição: "
                f"{', '.join(desconhecidos)}. "
                f"Use exatamente: {', '.join(sorted(niveis_validos))}."
            )

    rng = random.Random(seed)
    materias_filtro = list(materias) if materias else ([materia] if materia else [])

    candidatas = questao_repository.filtrar_questoes(
        sessao,
        serie=serie,
        materias=materias_filtro or None,
        conteudos=conteudos,
        adaptacoes=adaptacoes,
    )

    if not candidatas:
        raise RegraNegocio(
            "Nenhuma questão encontrada para os filtros informados. "
            "Verifique série/matérias/conteúdos ou popule o banco.",
            codigo="sem_questoes",
        )
    # Menos candidatas que o pedido gerava uma prova mais curta em silêncio. Falhamos
    # claro: melhor o gestor saber do que aplicar uma prova com menos questões sem querer.
    if len(candidatas) < quantidade:
        raise RegraNegocio(
            f"apenas {len(candidatas)} questão(ões) disponível(is) para os filtros, "
            f"mas {quantidade} foram solicitadas. Reduza a quantidade ou amplie os filtros.",
            codigo="questoes_insuficientes",
        )

    # Seleção curada por IA (quando informada): usa exatamente esses IDs, na ordem dada.
    # Os IDs já foram validados contra estas mesmas candidatas pelo ia_curadoria_service;
    # ainda assim filtramos aqui por segurança. Se nada casar, cai na seleção clássica.
    selecionadas: list[Questao] = []
    if selecao_ids:
        por_id = {q.id: q for q in candidatas}
        selecionadas = [por_id[i] for i in selecao_ids if i in por_id]
        # Cobertura incompleta (ex.: questão removida entre as duas buscas): descarta a
        # seleção curada e cai na seleção clássica, em vez de gerar uma prova curta.
        if len(selecionadas) < quantidade:
            selecionadas = []

    if not selecionadas:
        if distribuicao:
            selecionadas = _selecionar_por_distribuicao(
                candidatas, distribuicao, quantidade, rng
            )
        else:
            rng.shuffle(candidatas)
            selecionadas = candidatas[:quantidade]

    questoes_prova: list[QuestaoProva] = []
    contagem_nivel: dict[str, int] = {}

    for ordem, questao in enumerate(selecionadas, start=1):
        alternativas = list(questao.alternativas)
        if len(alternativas) > MAX_ALTERNATIVAS:
            raise RegraNegocio(
                f"questão {questao.id} tem {len(alternativas)} alternativas; "
                f"o máximo suportado é {MAX_ALTERNATIVAS}",
                codigo="questao_inconsistente",
            )
        rng.shuffle(alternativas)

        alts_prova: list[AlternativaProva] = []
        gabarito = None
        for letra, alt in zip(LETRAS, alternativas):
            alts_prova.append(
                AlternativaProva(letra=letra, texto=alt.texto, alternativa_id=alt.id)
            )
            if alt.correta:
                gabarito = letra

        if gabarito is None:
            raise RegraNegocio(
                f"questão {questao.id} não possui alternativa correta válida",
                codigo="questao_sem_gabarito",
            )

        contagem_nivel[questao.nivel.nome] = (
            contagem_nivel.get(questao.nivel.nome, 0) + 1
        )

        questoes_prova.append(
            QuestaoProva(
                ordem=ordem,
                questao_id=questao.id,
                enunciado=questao.enunciado,
                materia=questao.materia.nome,
                conteudo=questao.conteudo.nome,
                nivel=questao.nivel.nome,
                alternativas=alts_prova,
                gabarito=gabarito,
            )
        )

    materias_resultado = materias_filtro or sorted({q.materia for q in questoes_prova})

    return Prova(
        serie=serie,
        materias=materias_resultado,
        total=len(questoes_prova),
        distribuicao_real=contagem_nivel,
        questoes=questoes_prova,
    )
