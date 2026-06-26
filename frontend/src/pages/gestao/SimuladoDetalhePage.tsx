import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useLocation, useParams, useSearchParams } from "react-router-dom";

import { Button, Card, ConfirmDialog, Skeleton, StatusBadge } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { MonitorSimulado } from "./MonitorSimulado";
import {
  finalizarSimulado,
  gerarSimulado,
  liberarSimulado,
  obterSimulado,
  previewSimulado,
  removerQuestaoSimulado,
  trocarQuestaoSimulado,
} from "../../lib/api/simulados";
import type { FinalizacaoSimulado, PreviewSimulado, SimuladoResumo } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// C8 — Visualizar simulado (prévia com gabarito) + ações do ciclo (gerar/liberar/finalizar/editar).
export function SimuladoDetalhePage() {
  const { id } = useParams();
  const idNum = Number(id);
  const location = useLocation();
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const aba = searchParams.get("aba") === "monitor" ? "monitor" : "previa";

  const resumoInicial = (location.state as { resumo?: SimuladoResumo } | null)?.resumo;
  const resumoQuery = useQuery({
    queryKey: ["simulado", "resumo", idNum],
    queryFn: () => obterSimulado(idNum),
    initialData: resumoInicial,
  });
  const resumo = resumoQuery.data;
  const [confirmar, setConfirmar] = useState<"liberar" | "finalizar" | null>(null);
  const [resultado, setResultado] = useState<FinalizacaoSimulado | null>(null);
  const [erroAcao, setErroAcao] = useState<string | null>(null);

  const preview = useQuery({
    queryKey: ["simulado", "preview", idNum],
    queryFn: () => previewSimulado(idNum),
  });

  function atualizarResumo(r: SimuladoResumo) {
    queryClient.setQueryData(["simulado", "resumo", idNum], r);
  }
  function aplicarPreview(p: PreviewSimulado) {
    queryClient.setQueryData(["simulado", "preview", idNum], p);
    if (resumo) atualizarResumo({ ...resumo, total_questoes: p.questoes.length });
  }

  const status = resumo?.status;
  const editavel = status === "gerado";

  const gerar = useMutation({
    mutationFn: () => gerarSimulado(idNum),
    onSuccess: (r) => {
      atualizarResumo(r);
      preview.refetch();
      setErroAcao(null);
    },
    onError: () => setErroAcao(t.simuladoDetalhe.erroAcao),
  });
  const liberar = useMutation({
    mutationFn: () => liberarSimulado(idNum),
    onSuccess: (r) => {
      atualizarResumo(r);
      setConfirmar(null);
      setErroAcao(null);
    },
    onError: () => {
      setConfirmar(null);
      setErroAcao(t.simuladoDetalhe.erroAcao);
    },
  });
  const finalizar = useMutation({
    mutationFn: () => finalizarSimulado(idNum),
    onSuccess: (res) => {
      setResultado(res);
      if (resumo) atualizarResumo({ ...resumo, status: "finalizado" });
      setConfirmar(null);
      setErroAcao(null);
    },
    onError: () => {
      setConfirmar(null);
      setErroAcao(t.simuladoDetalhe.erroAcao);
    },
  });
  const remover = useMutation({
    mutationFn: (qid: number) => removerQuestaoSimulado(idNum, qid),
    onSuccess: aplicarPreview,
    onError: () => setErroAcao(t.simuladoDetalhe.erroAcao),
  });
  const trocar = useMutation({
    mutationFn: (qid: number) => trocarQuestaoSimulado(idNum, qid),
    onSuccess: aplicarPreview,
    onError: () => setErroAcao(t.simuladoDetalhe.erroAcao),
  });

  const editando = remover.isPending || trocar.isPending;
  const questoes = preview.data?.questoes ?? [];

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link to="/gestao/simulados" className="text-sm text-primary hover:underline">
            {t.simuladoDetalhe.voltar}
          </Link>
          <h1 className="text-2xl font-bold text-text mt-1">{resumo?.titulo ?? `Simulado #${idNum}`}</h1>
          <div className="mt-1.5">
            {status ? (
              <StatusBadge status={status} />
            ) : (
              <span className="text-xs text-text-muted">{t.simuladoDetalhe.statusDesconhecido}</span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {status === "rascunho" && (
            <Button variante="primary" onClick={() => gerar.mutate()} carregando={gerar.isPending}>
              {gerar.isPending ? t.simuladoDetalhe.gerando : t.simuladoDetalhe.gerar}
            </Button>
          )}
          {status === "gerado" && (
            <Button variante="primary" onClick={() => setConfirmar("liberar")}>
              {t.simuladoDetalhe.liberar}
            </Button>
          )}
          {status === "liberado" && (
            <Button variante="primary" onClick={() => setConfirmar("finalizar")}>
              {t.simuladoDetalhe.finalizar}
            </Button>
          )}
          {status === "finalizado" && (
            <Link to={`/gestao/ia/diagnostico/${idNum}`}>
              <Button variante="secondary">
                <Icon name="diagnostico" className="h-4 w-4" />
                {t.relatorios.diagnostico}
              </Button>
            </Link>
          )}
        </div>
      </div>

      {erroAcao && (
        <p role="alert" className="text-danger text-sm">
          {erroAcao}
        </p>
      )}

      {resultado && (
        <Card className="bg-success/10">
          <h2 className="font-display font-bold text-text">{t.simuladoDetalhe.resultadoTitulo}</h2>
          <p className="text-text-muted mt-1">
            {t.simuladoDetalhe.resultadoResumo(resultado.alunos_avaliados, resultado.total_questoes)}
          </p>
        </Card>
      )}

      <div className="inline-flex gap-1 p-1 rounded-2xl bg-surface-sunken shadow-clay-inset">
        {(["previa", "monitor"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSearchParams(tab === "monitor" ? { aba: "monitor" } : {})}
            aria-pressed={aba === tab}
            className={
              "px-4 h-9 rounded-xl text-sm font-display font-semibold transition-[background-color,box-shadow] " +
              (aba === tab ? "bg-surface text-primary shadow-clay-sm" : "text-text-muted hover:text-text")
            }
          >
            {tab === "previa" ? t.monitor.abaPrevia : t.monitor.abaMonitor}
          </button>
        ))}
      </div>

      {aba === "monitor" ? (
        <MonitorSimulado simuladoId={idNum} />
      ) : preview.isLoading ? (
        <Card className="space-y-3">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-20 w-full" />
        </Card>
      ) : preview.isError ? (
        <Card>
          <p className="text-danger">{t.simuladoDetalhe.erro}</p>
        </Card>
      ) : questoes.length === 0 ? (
        <Card>
          <p className="text-text-muted">{t.simuladoDetalhe.semQuestoes}</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {questoes.map((q) => (
            <Card key={q.questao_id} className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs text-text-muted">
                    {q.ordem}. {q.conteudo} · {q.nivel}
                  </p>
                  <p className="text-text font-medium mt-0.5">{q.enunciado}</p>
                </div>
                {editavel && (
                  <div className="flex gap-1 shrink-0">
                    <Button variante="ghost" tamanho="sm" onClick={() => trocar.mutate(q.questao_id)} disabled={editando}>
                      {t.simuladoDetalhe.trocar}
                    </Button>
                    <Button variante="ghost" tamanho="sm" onClick={() => remover.mutate(q.questao_id)} disabled={editando}>
                      {t.simuladoDetalhe.remover}
                    </Button>
                  </div>
                )}
              </div>
              <ul className="space-y-1.5">
                {q.alternativas.map((alt) => {
                  const correta = alt.correta || alt.letra === q.gabarito;
                  return (
                    <li
                      key={alt.alternativa_id}
                      className={"flex items-start gap-2 p-2 rounded-xl text-sm " + (correta ? "bg-success/10" : "")}
                    >
                      <span className={"font-semibold " + (correta ? "text-success" : "text-text-muted")}>{alt.letra}</span>
                      <span className="text-text">{alt.texto}</span>
                      {correta && <Icon name="check" className="h-4 w-4 text-success ml-auto shrink-0" />}
                    </li>
                  );
                })}
              </ul>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        aberto={confirmar === "liberar"}
        titulo={t.simuladoDetalhe.liberarTitulo}
        mensagem={t.simuladoDetalhe.liberarMsg}
        textoConfirmar={t.simuladoDetalhe.liberar}
        carregando={liberar.isPending}
        aoConfirmar={() => liberar.mutate()}
        aoCancelar={() => setConfirmar(null)}
      />
      <ConfirmDialog
        aberto={confirmar === "finalizar"}
        perigo
        titulo={t.simuladoDetalhe.finalizarTitulo}
        mensagem={t.simuladoDetalhe.finalizarMsg}
        textoConfirmar={t.simuladoDetalhe.finalizar}
        carregando={finalizar.isPending}
        aoConfirmar={() => finalizar.mutate()}
        aoCancelar={() => setConfirmar(null)}
      />
    </div>
  );
}
