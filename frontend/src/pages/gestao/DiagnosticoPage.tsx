import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";

import { Button, Card, Input, Skeleton } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { ApiError } from "../../lib/api/client";
import { diagnosticoDoSimulado } from "../../lib/api/ia";
import { t } from "../../i18n/pt-BR";

// C14 — Diagnóstico pedagógico (IA). Informe um simulado FINALIZADO → diagnóstico (IA ou fallback).
export function DiagnosticoPage() {
  const { simuladoId } = useParams();
  const [valor, setValor] = useState(simuladoId ?? "");
  const [buscarId, setBuscarId] = useState<number | null>(simuladoId ? Number(simuladoId) : null);

  const query = useQuery({
    queryKey: ["diagnostico", buscarId],
    enabled: buscarId !== null,
    queryFn: () => diagnosticoDoSimulado(buscarId as number),
  });

  const carregando = query.isFetching && buscarId !== null;
  const naoFinalizado =
    query.error instanceof ApiError && query.error.codigo === "simulado_nao_finalizado";
  const d = query.data;
  const ehIA = d ? d.modelo_versao !== "indisponivel" : false;

  return (
    <div className="space-y-5 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-text">{t.diagnostico.titulo}</h1>
        <p className="text-text-muted mt-0.5">{t.diagnostico.sub}</p>
      </div>

      <Card className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[180px]">
          <label htmlFor="sim" className="text-sm font-semibold text-text">
            {t.diagnostico.simuladoId}
          </label>
          <div className="mt-1.5">
            <Input
              id="sim"
              type="number"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
              placeholder={t.diagnostico.placeholder}
            />
          </div>
        </div>
        <Button variante="primary" disabled={!valor || carregando} carregando={carregando} onClick={() => setBuscarId(Number(valor))}>
          {carregando ? t.diagnostico.buscando : t.diagnostico.buscar}
        </Button>
      </Card>

      {carregando ? (
        <Card>
          <Skeleton className="h-24 w-full" />
        </Card>
      ) : naoFinalizado ? (
        <Card>
          <p className="text-text-muted">{t.diagnostico.naoFinalizado}</p>
        </Card>
      ) : query.isError ? (
        <Card>
          <p className="text-danger">{t.diagnostico.erro}</p>
        </Card>
      ) : d ? (
        <div className="space-y-4">
          <Card className="space-y-2">
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-lg font-bold text-text">{t.diagnostico.resumo}</h2>
              <span
                className={
                  "inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-chip " +
                  (ehIA ? "bg-secondary/40 text-secondary-ink" : "bg-surface-sunken text-text-muted")
                }
              >
                <Icon name="diagnostico" className="h-3.5 w-3.5" />
                {ehIA ? t.diagnostico.seloIA : t.diagnostico.seloFallback}
              </span>
            </div>
            <p className="text-text whitespace-pre-wrap">{d.resumo}</p>
          </Card>

          {d.pontos_fracos.length > 0 && (
            <Card>
              <h2 className="text-lg font-bold text-text mb-2">{t.diagnostico.pontosFracos}</h2>
              <div className="flex flex-wrap gap-2">
                {d.pontos_fracos.map((p, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-chip bg-danger/10 text-danger text-sm">
                    {p}
                  </span>
                ))}
              </div>
            </Card>
          )}

          <Card>
            <h2 className="text-lg font-bold text-text mb-2">{t.diagnostico.recomendacoes}</h2>
            {d.recomendacoes.length === 0 ? (
              <p className="text-text-muted text-sm">{t.diagnostico.semRecomendacoes}</p>
            ) : (
              <ul className="list-disc list-inside text-text space-y-1">
                {d.recomendacoes.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      ) : null}
    </div>
  );
}
