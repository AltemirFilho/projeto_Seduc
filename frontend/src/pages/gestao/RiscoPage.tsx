import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";

import { Button, Card, CORES_RISCO, Input, Skeleton } from "../../components/clay";
import { riscoDoAluno } from "../../lib/api/ia";
import { t } from "../../i18n/pt-BR";

// C15 — Risco de evasão (IA). Informe o id do aluno → predição (sklearn).
export function RiscoPage() {
  const { alunoId } = useParams();
  const [valor, setValor] = useState(alunoId ?? "");
  const [buscarId, setBuscarId] = useState<number | null>(alunoId ? Number(alunoId) : null);

  const query = useQuery({
    queryKey: ["risco", buscarId],
    enabled: buscarId !== null,
    queryFn: () => riscoDoAluno(buscarId as number),
  });

  const carregando = query.isFetching && buscarId !== null;
  const d = query.data;

  return (
    <div className="space-y-5 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-text">{t.risco.titulo}</h1>
        <p className="text-text-muted mt-0.5">{t.risco.sub}</p>
      </div>

      <Card className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[160px]">
          <label htmlFor="aluno" className="text-sm font-semibold text-text">
            {t.risco.alunoId}
          </label>
          <div className="mt-1.5">
            <Input
              id="aluno"
              type="number"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
              placeholder={t.risco.placeholder}
            />
          </div>
        </div>
        <Button variante="primary" disabled={!valor || carregando} carregando={carregando} onClick={() => setBuscarId(Number(valor))}>
          {carregando ? t.risco.buscando : t.risco.buscar}
        </Button>
      </Card>

      {carregando ? (
        <Card>
          <Skeleton className="h-20 w-full" />
        </Card>
      ) : query.isError ? (
        <Card>
          <p className="text-danger">{t.risco.erro}</p>
        </Card>
      ) : d ? (
        <Card className="space-y-4">
          <div className="flex items-center gap-4">
            <span
              className="px-4 py-2 rounded-chip font-bold text-lg"
              style={{ backgroundColor: CORES_RISCO[d.classificacao].bg, color: CORES_RISCO[d.classificacao].cor }}
            >
              {t.risco.classif[d.classificacao]}
            </span>
            <div>
              <p className="text-sm text-text-muted">{t.risco.score}</p>
              <p className="text-2xl font-display font-bold text-text">{Math.round(d.score_risco * 100)}%</p>
            </div>
          </div>
          <div>
            <p className="text-sm font-semibold text-text mb-1">{t.risco.fatores}</p>
            <ul className="list-disc list-inside text-text-muted space-y-0.5">
              {d.fatores.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          </div>
          <p className="text-xs text-text-muted">
            {t.risco.modelo}: {d.modelo_versao}
            {d.calculada_em ? ` · ${t.risco.calculadaEm} ${new Date(d.calculada_em).toLocaleString("pt-BR")}` : ""}
          </p>
        </Card>
      ) : null}
    </div>
  );
}
