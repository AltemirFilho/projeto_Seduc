from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions import DadosInvalidos, NaoEncontrado, RegraNegocio
from app.models import Alternativa, Conteudo, Materia, Questao
from app.repositories import etiqueta_repository, questao_repository

MAX_ALTERNATIVAS = 5


def _validar_alternativas(alternativas: list[dict]) -> list[Alternativa]:
    if not isinstance(alternativas, list) or len(alternativas) < 2:
        raise DadosInvalidos("informe ao menos 2 alternativas")
    if len(alternativas) > MAX_ALTERNATIVAS:
        raise DadosInvalidos(
            f"o máximo de alternativas por questão é {MAX_ALTERNATIVAS}"
        )
    corretas = [a for a in alternativas if a.get("correta")]
    if len(corretas) != 1:
        raise DadosInvalidos("marque exatamente 1 alternativa como correta")

    objs: list[Alternativa] = []
    for i, a in enumerate(alternativas, start=1):
        texto = (a.get("texto") or "").strip()
        if not texto:
            raise DadosInvalidos(f"alternativa {i} está sem texto")
        objs.append(
            Alternativa(texto=texto, correta=bool(a.get("correta")), ordem_original=i)
        )
    return objs


def cadastrar_questao(
    sessao: Session,
    *,
    enunciado: str,
    serie: str,
    materia: str,
    conteudo: str,
    nivel: str,
    alternativas: list[dict],
    adaptacoes: list[str] | None = None,
    imagem_url: str | None = None,
) -> Questao:
    enunciado = (enunciado or "").strip()
    if not enunciado:
        raise DadosInvalidos("enunciado é obrigatório")

    serie_obj = etiqueta_repository.serie_por_nome(sessao, serie)
    if serie_obj is None:
        raise NaoEncontrado(f"série inexistente: '{serie}'")

    nivel_obj = etiqueta_repository.nivel_por_nome(sessao, nivel)
    if nivel_obj is None:
        raise NaoEncontrado(f"nível inexistente: '{nivel}'")

    objs_alt = _validar_alternativas(alternativas)

    materia_obj = etiqueta_repository.materia_por_nome(sessao, materia)
    if materia_obj is None:
        materia_obj = Materia(nome=materia.strip())
        sessao.add(materia_obj)
        sessao.flush()

    conteudo_nome = (conteudo or "").strip()
    if not conteudo_nome:
        raise DadosInvalidos("conteúdo é obrigatório")
    conteudo_obj = etiqueta_repository.conteudo_por_nome(
        sessao, conteudo_nome, materia_obj.id
    )
    if conteudo_obj is None:
        conteudo_obj = Conteudo(nome=conteudo_nome, materia=materia_obj)
        sessao.add(conteudo_obj)
        sessao.flush()

    questao = Questao(
        enunciado=enunciado,
        imagem_url=imagem_url,
        serie=serie_obj,
        materia=materia_obj,
        conteudo=conteudo_obj,
        nivel=nivel_obj,
        adaptacoes=adaptacoes or [],
        alternativas=objs_alt,
    )
    sessao.add(questao)
    sessao.commit()
    sessao.refresh(questao)
    return questao


def obter_questao(sessao: Session, questao_id: int) -> Questao:
    questao = sessao.get(Questao, questao_id)
    if questao is None:
        raise NaoEncontrado(f"questão {questao_id} não encontrada")
    return questao


def _resolver_materia_conteudo(
    sessao: Session, questao: Questao, materia: str | None, conteudo: str | None
) -> None:
    """Reaponta matéria/conteúdo da questão (criando se necessário, como no cadastro).
    Conteúdo é sempre resolvido sob a matéria final, para não ficar órfão de outra matéria."""
    materia_nome = (materia if materia is not None else questao.materia.nome).strip()
    if not materia_nome:
        raise DadosInvalidos("matéria não pode ficar vazia")
    materia_obj = etiqueta_repository.materia_por_nome(sessao, materia_nome)
    if materia_obj is None:
        materia_obj = Materia(nome=materia_nome)
        sessao.add(materia_obj)
        sessao.flush()

    conteudo_nome = (conteudo if conteudo is not None else questao.conteudo.nome).strip()
    if not conteudo_nome:
        raise DadosInvalidos("conteúdo não pode ficar vazio")
    conteudo_obj = etiqueta_repository.conteudo_por_nome(
        sessao, conteudo_nome, materia_obj.id
    )
    if conteudo_obj is None:
        conteudo_obj = Conteudo(nome=conteudo_nome, materia=materia_obj)
        sessao.add(conteudo_obj)
        sessao.flush()

    questao.materia = materia_obj
    questao.conteudo = conteudo_obj


def editar_questao(
    sessao: Session,
    *,
    questao_id: int,
    enunciado: str | None = None,
    serie: str | None = None,
    materia: str | None = None,
    conteudo: str | None = None,
    nivel: str | None = None,
    adaptacoes: list[str] | None = None,
    imagem_url: str | None = None,
    alternativas: list[dict] | None = None,
) -> Questao:
    """Edição parcial (PATCH): campos com None não são alterados.

    Questão já usada em simulado é congelada: editá-la corromperia o caderno/gabarito já
    gerado (SimuladoQuestao.alternativas_ordem) e a correção persistida.
    """
    questao = obter_questao(sessao, questao_id)
    if questao_repository.questao_em_uso(sessao, questao_id):
        raise RegraNegocio(
            "a questão já foi usada em um simulado e não pode mais ser editada",
            codigo="questao_em_uso",
        )

    if enunciado is not None:
        novo = enunciado.strip()
        if not novo:
            raise DadosInvalidos("enunciado não pode ficar vazio")
        questao.enunciado = novo

    if serie is not None:
        serie_obj = etiqueta_repository.serie_por_nome(sessao, serie)
        if serie_obj is None:
            raise NaoEncontrado(f"série inexistente: '{serie}'")
        questao.serie = serie_obj

    if nivel is not None:
        nivel_obj = etiqueta_repository.nivel_por_nome(sessao, nivel)
        if nivel_obj is None:
            raise NaoEncontrado(f"nível inexistente: '{nivel}'")
        questao.nivel = nivel_obj

    if materia is not None or conteudo is not None:
        _resolver_materia_conteudo(sessao, questao, materia, conteudo)

    if imagem_url is not None:
        questao.imagem_url = imagem_url

    if adaptacoes is not None:
        if not isinstance(adaptacoes, list):
            raise DadosInvalidos("adaptacoes deve ser uma lista")
        questao.adaptacoes = adaptacoes

    if alternativas is not None:
        questao.alternativas = _validar_alternativas(alternativas)

    sessao.commit()
    sessao.refresh(questao)
    return questao
