import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Card, Skeleton } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { ApiError } from "../../lib/api/client";
import { meuResultado } from "../../lib/api/simulados";
import type { MeuResultado } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// B4 — Resultado do simulado (real: GET /simulados/{id}/meu-resultado, só FINALIZADO).
export function ResultadoAlunoPage() {
  const { id } = useParams();
  const idNum = Number(id);
  const query = useQuery({ queryKey: ["meu-resultado", idNum], queryFn: () => meuResultado(idNum) });

  const naoFinalizado =
    query.error instanceof ApiError && query.error.codigo === "simulado_nao_finalizado";

  return (
    <div className="max-w-2xl space-y-5">
      <Link to="/app/simulados" className="text-sm text-primary hover:underline">
        {t.resultadoAluno.voltar}
      </Link>
      <h1 className="text-2xl font-bold text-text">{t.resultadoAluno.titulo}</h1>

      {query.isLoading ? (
        <Card className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-24 w-full" />
        </Card>
      ) : naoFinalizado ? (
        <Card>
          <p className="text-text-muted">{t.resultadoAluno.naoFinalizado}</p>
        </Card>
      ) : query.isError ? (
        <Card>
          <p className="text-danger">{t.resultadoAluno.erro}</p>
        </Card>
      ) : query.data ? (
        <Resultado r={query.data} />
      ) : null}
    </div>
  );
}

function Resultado({ r }: { r: MeuResultado }) {
  const pct = r.total_questoes ? Math.round((r.acertos / r.total_questoes) * 100) : 0;
  return (
    <>
      <Card className="flex items-center gap-5">
        <div className="grid place-items-center h-20 w-20 rounded-full bg-primary text-on-primary shrink-0">
          <span className="font-display text-2xl font-bold">{r.nota.toFixed(1)}</span>
        </div>
        <div>
          <p className="text-sm text-text-muted">{t.resultadoAluno.nota}</p>
          <p className="text-text font-medium">
            {t.resultadoAluno.resumo(r.acertos, r.total_questoes)} · {pct}%
          </p>
        </div>
      </Card>

      <div className="space-y-3">
        {r.questoes.map((q) => (
          <Card key={q.questao_id} className="space-y-2">
            <div className="flex items-start gap-2">
              <span className={q.acertou ? "text-success" : q.acertou === false ? "text-danger" : "text-text-muted"}>
                <Icon name={q.acertou ? "check" : "fechar"} className="h-5 w-5 mt-0.5" />
              </span>
              <div className="min-w-0">
                <p className="text-xs text-text-muted">
                  {q.ordem}. {q.conteudo}
                </p>
                <p className="text-text font-medium">{q.enunciado}</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm pl-7">
              <span className="text-text-muted">
                {t.resultadoAluno.suaResposta}:{" "}
                <strong className={q.acertou ? "text-success" : "text-text"}>
                  {q.sua_resposta ?? t.resultadoAluno.naoRespondeu}
                </strong>
              </span>
              <span className="text-text-muted">
                {t.resultadoAluno.gabarito}: <strong className="text-success">{q.gabarito}</strong>
              </span>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}
