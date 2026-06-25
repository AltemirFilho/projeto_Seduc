from __future__ import annotations

import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import PerfilUsuario, StatusSimulado
from app.exceptions import DadosInvalidos, NaoEncontrado, PermissaoNegada, RegraNegocio
from app.models import Aluno, Alternativa, Resposta, Simulado, SimuladoQuestao, Usuario
from app.repositories import questao_repository, usuario_repository
from app.services import ia_curadoria_service, prova_service

LETRAS = "ABCDE"


def _obter_simulado(sessao: Session, simulado_id: int) -> Simulado:
    simulado = sessao.get(Simulado, simulado_id)
    if simulado is None:
        raise NaoEncontrado(f"simulado {simulado_id} não encontrado")
    return simulado


def _exigir_dono(simulado: Simulado, solicitante: Usuario) -> None:
    """Só o gestor que criou o simulado (ou um admin) pode operá-lo. A autorização por
    PERFIL (require_gestor) já roda no router; aqui garantimos a POSSE do recurso, para
    um gestor não mexer no simulado de outro."""
    if solicitante.perfil == PerfilUsuario.ADMIN:
        return
    if simulado.gestor_id == solicitante.id:
        return
    raise PermissaoNegada(
        "você não é o gestor responsável por este simulado",
        codigo="nao_e_dono",
    )


def criar_simulado(
    sessao: Session,
    *,
    gestor_id: int,
    turma_id: int,
    titulo: str,
    parametros: dict,
) -> Simulado:
    simulado = Simulado(
        gestor_id=gestor_id,
        turma_id=turma_id,
        titulo=titulo,
        parametros_json=parametros,
        status=StatusSimulado.RASCUNHO,
    )
    sessao.add(simulado)
    sessao.commit()
    sessao.refresh(simulado)
    return simulado


def gerar_e_persistir(
    sessao: Session,
    *,
    simulado_id: int,
    solicitante: Usuario,
    seed: int | None = None,
) -> Simulado:
    simulado = _obter_simulado(sessao, simulado_id)
    _exigir_dono(simulado, solicitante)
    if simulado.status not in (StatusSimulado.RASCUNHO, StatusSimulado.GERADO):
        raise RegraNegocio(
            f"simulado não pode ser gerado no status '{simulado.status.value}'"
        )

    p = simulado.parametros_json or {}
    if not p.get("serie") or not (p.get("materia") or p.get("materias")):
        raise DadosInvalidos("parâmetros do simulado precisam de 'serie' e 'materia(s)'")

    # Curadoria por IA (quando habilitada): a IA escolhe e ordena as questões; em
    # timeout/erro/baixa confiança, selecao_ids volta None e o prova_service usa a
    # seleção clássica. A meta registra qual fonte foi usada.
    selecao_ids, curadoria_meta = ia_curadoria_service.selecionar_questoes(
        sessao,
        serie=p["serie"],
        materia=p.get("materia"),
        materias=p.get("materias"),
        conteudos=p.get("conteudos"),
        distribuicao=p.get("distribuicao"),
        quantidade=p.get("quantidade", 10),
        adaptacoes=p.get("adaptacoes"),
    )

    prova = prova_service.gerar_prova(
        sessao,
        serie=p["serie"],
        materia=p.get("materia"),
        materias=p.get("materias"),
        conteudos=p.get("conteudos"),
        distribuicao=p.get("distribuicao"),
        quantidade=p.get("quantidade", 10),
        adaptacoes=p.get("adaptacoes"),
        seed=seed if seed is not None else p.get("seed"),
        selecao_ids=selecao_ids,
    )

    # Registra a fonte da curadoria nos parâmetros (reatribui o dict para o SQLAlchemy
    # detectar a mudança na coluna JSON). Aditivo: não altera o shape do contrato.
    simulado.parametros_json = {**p, "ia_curadoria": curadoria_meta}

    simulado.questoes.clear()
    sessao.flush()

    for q in prova.questoes:
        simulado.questoes.append(
            SimuladoQuestao(
                questao_id=q.questao_id,
                ordem_questao=q.ordem,
                alternativas_ordem=[a.alternativa_id for a in q.alternativas],
            )
        )

    simulado.status = StatusSimulado.GERADO
    sessao.commit()
    sessao.refresh(simulado)
    return simulado


def liberar(sessao: Session, *, simulado_id: int, solicitante: Usuario) -> Simulado:
    simulado = _obter_simulado(sessao, simulado_id)
    _exigir_dono(simulado, solicitante)
    if simulado.status != StatusSimulado.GERADO:
        raise RegraNegocio("apenas simulados GERADOS podem ser liberados")
    simulado.status = StatusSimulado.LIBERADO
    sessao.commit()
    sessao.refresh(simulado)
    return simulado


def montar_questoes(
    sessao: Session, *, simulado_id: int, incluir_gabarito: bool = False
) -> list[dict]:
    simulado = _obter_simulado(sessao, simulado_id)

    questoes: list[dict] = []
    for sq in simulado.questoes:
        questao = sq.questao
        alt_por_id = {a.id: a for a in questao.alternativas}

        alternativas: list[dict] = []
        gabarito = None
        for letra, alt_id in zip(LETRAS, sq.alternativas_ordem):
            alt = alt_por_id.get(alt_id)
            if alt is None:
                raise RegraNegocio(
                    f"a ordem de alternativas do simulado referencia uma "
                    f"alternativa inexistente (questão {questao.id})",
                    codigo="simulado_inconsistente",
                )
            item = {"letra": letra, "texto": alt.texto, "alternativa_id": alt.id}
            if incluir_gabarito:
                item["correta"] = alt.correta
            if alt.correta:
                gabarito = letra
            alternativas.append(item)

        if incluir_gabarito and gabarito is None:
            raise RegraNegocio(
                f"questão {questao.id} do simulado está sem gabarito válido",
                codigo="simulado_inconsistente",
            )

        q = {
            "ordem": sq.ordem_questao,
            "questao_id": questao.id,
            "enunciado": questao.enunciado,
            "conteudo": questao.conteudo.nome,
            "nivel": questao.nivel.nome,
            "alternativas": alternativas,
        }
        if incluir_gabarito:
            q["gabarito"] = gabarito
        questoes.append(q)

    return questoes


def montar_questoes_preview(
    sessao: Session, *, simulado_id: int, solicitante: Usuario
) -> list[dict]:
    """Prévia COM gabarito — restrita ao gestor dono (ou admin)."""
    simulado = _obter_simulado(sessao, simulado_id)
    _exigir_dono(simulado, solicitante)
    return montar_questoes(sessao, simulado_id=simulado_id, incluir_gabarito=True)


def montar_questoes_do_aluno(
    sessao: Session, *, simulado_id: int, solicitante: Usuario
) -> list[dict]:
    """Questões SEM gabarito (a visão de quem responde).

    Isolamento: um aluno só enxerga simulado LIBERADO da PRÓPRIA turma. O gestor dono e o
    admin podem inspecionar essa visão (para conferência). Qualquer outro perfil é barrado.
    """
    simulado = _obter_simulado(sessao, simulado_id)
    aluno = usuario_repository.aluno_do_usuario(sessao, solicitante.id)
    if aluno is not None:
        if simulado.status != StatusSimulado.LIBERADO:
            raise PermissaoNegada(
                "o simulado ainda não foi liberado", codigo="simulado_nao_liberado"
            )
        if aluno.turma_id != simulado.turma_id:
            raise PermissaoNegada(
                "este simulado não pertence à sua turma", codigo="fora_da_turma"
            )
    elif solicitante.perfil == PerfilUsuario.ADMIN:
        pass
    elif (
        solicitante.perfil == PerfilUsuario.GESTOR
        and simulado.gestor_id == solicitante.id
    ):
        pass
    else:
        raise PermissaoNegada(
            "você não tem acesso a este simulado", codigo="sem_acesso"
        )
    return montar_questoes(sessao, simulado_id=simulado_id, incluir_gabarito=False)


def registrar_resposta(
    sessao: Session,
    *,
    aluno_id: int,
    simulado_id: int,
    questao_id: int,
    alternativa_id: int,
) -> Resposta:
    simulado = _obter_simulado(sessao, simulado_id)
    if simulado.status != StatusSimulado.LIBERADO:
        raise RegraNegocio("o simulado não está liberado para respostas")

    aluno = sessao.get(Aluno, aluno_id)
    if aluno is None:
        raise NaoEncontrado(f"aluno {aluno_id} não encontrado")
    if aluno.turma_id != simulado.turma_id:
        raise PermissaoNegada(
            "você não pertence à turma deste simulado", codigo="fora_da_turma"
        )

    pertence = sessao.scalar(
        select(SimuladoQuestao).where(
            SimuladoQuestao.simulado_id == simulado_id,
            SimuladoQuestao.questao_id == questao_id,
        )
    )
    if pertence is None:
        raise DadosInvalidos("a questão não pertence a este simulado")

    alternativa = sessao.get(Alternativa, alternativa_id)
    if alternativa is None or alternativa.questao_id != questao_id:
        raise DadosInvalidos("alternativa inválida para a questão")

    resposta = sessao.scalar(
        select(Resposta).where(
            Resposta.aluno_id == aluno_id,
            Resposta.simulado_id == simulado_id,
            Resposta.questao_id == questao_id,
        )
    )
    if resposta is None:
        resposta = Resposta(
            aluno_id=aluno_id,
            simulado_id=simulado_id,
            questao_id=questao_id,
            alternativa_id=alternativa_id,
            correta=alternativa.correta,
        )
        sessao.add(resposta)
    else:
        resposta.alternativa_id = alternativa_id
        resposta.correta = alternativa.correta

    sessao.commit()
    sessao.refresh(resposta)
    return resposta


def finalizar_e_corrigir(
    sessao: Session, *, simulado_id: int, solicitante: Usuario
) -> dict:
    simulado = _obter_simulado(sessao, simulado_id)
    _exigir_dono(simulado, solicitante)
    if simulado.status != StatusSimulado.LIBERADO:
        raise RegraNegocio(
            "só é possível finalizar um simulado que esteja LIBERADO"
        )

    total_questoes = len(simulado.questoes)
    respostas = sessao.scalars(
        select(Resposta).where(Resposta.simulado_id == simulado_id)
    ).all()

    por_aluno: dict[int, dict] = {}
    for r in respostas:
        d = por_aluno.setdefault(r.aluno_id, {"acertos": 0, "respondidas": 0})
        d["respondidas"] += 1
        if r.correta:
            d["acertos"] += 1

    resultados = []
    for aluno_id, d in por_aluno.items():
        nota = round(10 * d["acertos"] / total_questoes, 2) if total_questoes else 0.0
        resultados.append(
            {
                "aluno_id": aluno_id,
                "acertos": d["acertos"],
                "respondidas": d["respondidas"],
                "total_questoes": total_questoes,
                "nota": nota,
            }
        )

    simulado.status = StatusSimulado.FINALIZADO
    sessao.commit()

    return {
        "simulado_id": simulado_id,
        "total_questoes": total_questoes,
        "alunos_avaliados": len(resultados),
        "resultados": resultados,
    }


def _exigir_editavel(simulado: Simulado) -> None:
    if simulado.status != StatusSimulado.GERADO:
        raise RegraNegocio(
            "só é possível editar o simulado no status 'gerado' (antes de liberar)"
        )


def _validar_questao_para_simulado(questao) -> None:
    """Mesmas guardas que prova_service aplica ao gerar: teto de alternativas e gabarito."""
    if len(questao.alternativas) > prova_service.MAX_ALTERNATIVAS:
        raise RegraNegocio(
            f"questão {questao.id} tem mais de {prova_service.MAX_ALTERNATIVAS} "
            f"alternativas e não pode entrar no simulado",
            codigo="questao_inconsistente",
        )
    if not any(a.correta for a in questao.alternativas):
        raise RegraNegocio(
            f"questão {questao.id} não possui alternativa correta",
            codigo="questao_sem_gabarito",
        )


def remover_questao(
    sessao: Session, *, simulado_id: int, questao_id: int, solicitante: Usuario
) -> Simulado:
    simulado = _obter_simulado(sessao, simulado_id)
    _exigir_dono(simulado, solicitante)
    _exigir_editavel(simulado)

    alvo = next((sq for sq in simulado.questoes if sq.questao_id == questao_id), None)
    if alvo is None:
        raise NaoEncontrado("questão não está neste simulado")
    if len(simulado.questoes) <= 1:
        raise RegraNegocio("o simulado precisa manter ao menos 1 questão")

    simulado.questoes.remove(alvo)
    sessao.flush()
    for i, sq in enumerate(
        sorted(simulado.questoes, key=lambda x: x.ordem_questao), start=1
    ):
        sq.ordem_questao = i
    sessao.commit()
    sessao.refresh(simulado)
    return simulado


def trocar_questao(
    sessao: Session,
    *,
    simulado_id: int,
    questao_id: int,
    solicitante: Usuario,
    seed: int | None = None,
) -> Simulado:
    simulado = _obter_simulado(sessao, simulado_id)
    _exigir_dono(simulado, solicitante)
    _exigir_editavel(simulado)

    alvo = next((sq for sq in simulado.questoes if sq.questao_id == questao_id), None)
    if alvo is None:
        raise NaoEncontrado("questão não está neste simulado")

    nivel_alvo = alvo.questao.nivel.nome

    p = simulado.parametros_json or {}
    candidatas = questao_repository.filtrar_questoes(
        sessao,
        serie=p.get("serie"),
        materia=p.get("materia"),
        materias=p.get("materias"),
        conteudos=p.get("conteudos"),
        adaptacoes=p.get("adaptacoes"),
    )
    presentes = {sq.questao_id for sq in simulado.questoes}
    disponiveis = [q for q in candidatas if q.id not in presentes]
    if not disponiveis:
        raise RegraNegocio(
            "não há outra questão disponível para troca com esses filtros"
        )

    # Preferimos manter o mesmo nível de dificuldade da questão trocada.
    mesmo_nivel = [q for q in disponiveis if q.nivel.nome == nivel_alvo]
    pool = mesmo_nivel or disponiveis

    rng = random.Random(seed)
    nova = rng.choice(pool)
    _validar_questao_para_simulado(nova)
    alternativas = list(nova.alternativas)
    rng.shuffle(alternativas)

    alvo.questao_id = nova.id
    alvo.alternativas_ordem = [a.id for a in alternativas]
    sessao.commit()
    sessao.refresh(simulado)
    return simulado
