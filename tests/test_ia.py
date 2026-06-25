"""Testes da curadoria de simulado por IA (Frente B).

Não chamam a Claude API de verdade: monkeypatcham `claude.disponivel` e
`claude.completar_json` para exercitar o serviço e o fallback de forma determinística.
Com a IA desligada (padrão), a geração continua idêntica à seleção clássica.
"""

from app.integrations import claude as claude_mod
from app.repositories import questao_repository


def _criar_simulado(client, h_gestor, turma_id, *, quantidade=3, seed=7):
    r = client.post(
        "/simulados",
        headers=h_gestor,
        json={
            "turma_id": turma_id,
            "titulo": "Simulado IA",
            "serie": "9º ano",
            "materia": "Matemática",
            "quantidade": quantidade,
            "seed": seed,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _gerar(client, h_gestor, sid):
    return client.post(f"/simulados/{sid}/gerar", headers=h_gestor, json={}).json()


def _ids_candidatas(Sessao):
    with Sessao() as s:
        cands = questao_repository.filtrar_questoes(
            s, serie="9º ano", materias=["Matemática"]
        )
        return [q.id for q in cands]


def _ids_por_nivel(Sessao):
    with Sessao() as s:
        cands = questao_repository.filtrar_questoes(
            s, serie="9º ano", materias=["Matemática"]
        )
        por_nivel: dict[str, list[int]] = {}
        for q in cands:
            por_nivel.setdefault(q.nivel.nome, []).append(q.id)
        return por_nivel


def test_disponivel_so_com_flag_e_chave(monkeypatch):
    from app.config import settings

    # Flag desligada: indisponível (e o backend usa o fallback clássico).
    monkeypatch.setattr(settings, "ia_curadoria_habilitada", False)
    assert claude_mod.disponivel() is False

    # Flag ligada mas sem chave: ainda indisponível.
    monkeypatch.setattr(settings, "ia_curadoria_habilitada", True)
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    assert claude_mod.disponivel() is False


def test_gerar_sem_ia_marca_fonte_classico(client, h_gestor, dados):
    sid = _criar_simulado(client, h_gestor, dados["turma_id"])
    corpo = _gerar(client, h_gestor, sid)
    assert corpo["status"] == "gerado"
    meta = corpo["parametros"]["ia_curadoria"]
    assert meta["fonte"] == "classico"
    assert meta["motivo"] == "ia_desabilitada"


def test_ia_curada_usa_selecao_e_ordem(client, h_gestor, dados, Sessao, monkeypatch):
    ids = _ids_candidatas(Sessao)
    assert len(ids) >= 5
    escolhidos = [ids[4], ids[2], ids[0]]  # ordem proposital, fora da ordem natural

    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(
        claude_mod,
        "completar_json",
        lambda **kwargs: {"questao_ids": escolhidos, "confianca": 0.9},
    )

    sid = _criar_simulado(client, h_gestor, dados["turma_id"], quantidade=3)
    corpo = _gerar(client, h_gestor, sid)
    assert corpo["parametros"]["ia_curadoria"]["fonte"] == "ia"
    assert corpo["parametros"]["ia_curadoria"]["confianca"] == 0.9

    preview = client.get(
        f"/simulados/{sid}/preview", headers=h_gestor
    ).json()["questoes"]
    assert [q["questao_id"] for q in preview] == escolhidos


def test_ia_selecao_invalida_cai_no_classico(client, h_gestor, dados, monkeypatch):
    # IDs que não existem nas candidatas: a validação derruba para o clássico.
    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(
        claude_mod,
        "completar_json",
        lambda **kwargs: {"questao_ids": [99991, 99992, 99993], "confianca": 0.9},
    )
    sid = _criar_simulado(client, h_gestor, dados["turma_id"], quantidade=3)
    corpo = _gerar(client, h_gestor, sid)
    assert corpo["status"] == "gerado"
    assert corpo["total_questoes"] == 3
    meta = corpo["parametros"]["ia_curadoria"]
    assert meta["fonte"] == "classico"
    assert meta["motivo"] == "selecao_ia_invalida"


def test_ia_baixa_confianca_cai_no_classico(
    client, h_gestor, dados, Sessao, monkeypatch
):
    ids = _ids_candidatas(Sessao)
    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(
        claude_mod,
        "completar_json",
        lambda **kwargs: {"questao_ids": ids[:3], "confianca": 0.2},
    )
    sid = _criar_simulado(client, h_gestor, dados["turma_id"], quantidade=3)
    corpo = _gerar(client, h_gestor, sid)
    meta = corpo["parametros"]["ia_curadoria"]
    assert meta["fonte"] == "classico"
    assert meta["motivo"] == "baixa_confianca"
    assert meta["confianca"] == 0.2


def test_ia_falha_cai_no_classico(client, h_gestor, dados, monkeypatch):
    def _boom(**kwargs):
        raise claude_mod.IAIndisponivel("timeout simulado")

    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(claude_mod, "completar_json", _boom)
    sid = _criar_simulado(client, h_gestor, dados["turma_id"], quantidade=3)
    corpo = _gerar(client, h_gestor, sid)
    meta = corpo["parametros"]["ia_curadoria"]
    assert meta["fonte"] == "classico"
    # Motivo estável (sem vazar o erro cru da Anthropic em parametros_json).
    assert meta["motivo"] == "ia_falhou"


def test_ia_confianca_invalida_cai_no_classico(client, h_gestor, dados, Sessao, monkeypatch):
    # Confiança ausente/None deve falhar fechado, não passar batido pelo piso.
    ids = _ids_candidatas(Sessao)
    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(
        claude_mod,
        "completar_json",
        lambda **kwargs: {"questao_ids": ids[:3], "confianca": None},
    )
    sid = _criar_simulado(client, h_gestor, dados["turma_id"], quantidade=3)
    corpo = _gerar(client, h_gestor, sid)
    meta = corpo["parametros"]["ia_curadoria"]
    assert meta["fonte"] == "classico"
    assert meta["motivo"] == "confianca_invalida"


def test_ia_distribuicao_nao_atendida_cai_no_classico(
    client, h_gestor, dados, Sessao, monkeypatch
):
    # Distribuição pede maioria 'Fácil', mas a IA devolve só Difícil+Médio -> rejeita.
    por_nivel = _ids_por_nivel(Sessao)
    escolhidos = por_nivel["Difícil"][:2] + por_nivel["Médio"][:1]
    monkeypatch.setattr(claude_mod, "disponivel", lambda: True)
    monkeypatch.setattr(
        claude_mod,
        "completar_json",
        lambda **kwargs: {"questao_ids": escolhidos, "confianca": 0.9},
    )
    r = client.post(
        "/simulados",
        headers=h_gestor,
        json={
            "turma_id": dados["turma_id"],
            "titulo": "Simulado IA dist",
            "serie": "9º ano",
            "materia": "Matemática",
            "quantidade": 3,
            "distribuicao": {"Fácil": 0.6, "Médio": 0.2, "Difícil": 0.2},
            "seed": 7,
        },
    )
    assert r.status_code == 201, r.text
    corpo = _gerar(client, h_gestor, r.json()["id"])
    assert corpo["total_questoes"] == 3
    meta = corpo["parametros"]["ia_curadoria"]
    assert meta["fonte"] == "classico"
    assert meta["motivo"] == "distribuicao_nao_atendida"
