import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Button, Card, Select, Skeleton, StatusBadge } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { listarSimulados } from "../../lib/api/simulados";
import { t } from "../../i18n/pt-BR";

// C7 — Simulados. GET /simulados (lista real, filtro por status).
export function SimuladosPage() {
  const [status, setStatus] = useState("");
  const query = useQuery({
    queryKey: ["simulados", status],
    queryFn: () => listarSimulados({ status: status || undefined }),
  });
  const simulados = query.data?.dados ?? [];

  return (
    <div className="space-y-5 max-w-4xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-text">{t.simulados.titulo}</h1>
        <Link to="/gestao/simulados/novo">
          <Button variante="primary" tamanho="sm">
            <Icon name="simulados" className="h-4 w-4" />
            {t.simulados.novo}
          </Button>
        </Link>
      </div>

      <Card className="p-4 max-w-xs">
        <Select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          aria-label={t.simulados.filtroStatus}
        >
          <option value="">{t.simulados.todosStatus}</option>
          <option value="rascunho">{t.statusSimulado.rascunho}</option>
          <option value="gerado">{t.statusSimulado.gerado}</option>
          <option value="liberado">{t.statusSimulado.liberado}</option>
          <option value="finalizado">{t.statusSimulado.finalizado}</option>
        </Select>
      </Card>

      {query.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <Skeleton className="h-12 w-full" />
            </Card>
          ))}
        </div>
      ) : query.isError ? (
        <Card>
          <p className="text-danger">{t.simulados.erro}</p>
        </Card>
      ) : simulados.length === 0 ? (
        <Card>
          <p className="text-text-muted text-center py-6">{t.simulados.vazio}</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {simulados.map((s) => (
            <Card key={s.id} className="flex flex-wrap items-center gap-3">
              <div className="min-w-0">
                <p className="font-display font-semibold text-text truncate">{s.titulo}</p>
                <p className="text-xs text-text-muted mt-0.5">
                  {t.simulados.turma} {s.turma ?? s.turma_id} · {s.total_questoes} {t.simulados.questoes}
                </p>
              </div>
              <div className="ml-auto flex items-center gap-3">
                <StatusBadge status={s.status} />
                <Link to={`/gestao/simulados/${s.id}`} state={{ resumo: s }}>
                  <Button variante="secondary" tamanho="sm">
                    {t.simulados.abrir}
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
