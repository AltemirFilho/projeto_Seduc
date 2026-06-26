import { useQuery } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

import { Button, Card, Skeleton, StatusBadge } from "../../components/clay";
import { listarSimuladosDisponiveis } from "../../lib/api/simulados";
import { t } from "../../i18n/pt-BR";

// B2 — Meus simulados e notas. Abas Disponíveis / Finalizados (GET /simulados/disponiveis).
export function MeusSimuladosPage() {
  const query = useQuery({
    queryKey: ["aluno", "simulados"],
    queryFn: listarSimuladosDisponiveis,
  });
  const todos = query.data?.dados ?? [];
  const disponiveis = todos.filter((s) => s.status === "liberado");
  const finalizados = todos.filter((s) => s.status === "finalizado");
  const [aba, setAba] = useState<"disponiveis" | "finalizados">("disponiveis");
  const lista = aba === "disponiveis" ? disponiveis : finalizados;

  return (
    <div className="space-y-5 max-w-3xl">
      <h1 className="text-2xl font-bold text-text">{t.aluno.meusSimulados}</h1>

      <div className="inline-flex p-1 rounded-chip bg-surface-sunken shadow-clay-inset">
        <Aba ativa={aba === "disponiveis"} onClick={() => setAba("disponiveis")}>
          {t.aluno.disponiveis} ({disponiveis.length})
        </Aba>
        <Aba ativa={aba === "finalizados"} onClick={() => setAba("finalizados")}>
          {t.aluno.finalizados} ({finalizados.length})
        </Aba>
      </div>

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
          <p className="text-danger">{t.aluno.erro}</p>
        </Card>
      ) : lista.length === 0 ? (
        <Card>
          <p className="text-text-muted text-center py-6">
            {aba === "disponiveis" ? t.aluno.semDisponiveis : t.aluno.semFinalizados}
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {lista.map((s) => (
            <Card key={s.id} className="flex flex-wrap items-center gap-3">
              <div className="min-w-0">
                <p className="font-display font-semibold text-text truncate">{s.titulo}</p>
                <p className="text-xs text-text-muted mt-0.5">
                  {s.total_questoes} {t.aluno.questoes}
                </p>
              </div>
              <div className="ml-auto flex items-center gap-3">
                <StatusBadge status={s.status} />
                {s.status === "liberado" ? (
                  <Link to={`/app/simulados/${s.id}/responder`} state={{ titulo: s.titulo }}>
                    <Button variante="primary" tamanho="sm">
                      {t.aluno.responder}
                    </Button>
                  </Link>
                ) : (
                  <Link to={`/app/resultados/${s.id}`}>
                    <Button variante="secondary" tamanho="sm">
                      {t.aluno.verResultado}
                    </Button>
                  </Link>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function Aba({ ativa, onClick, children }: { ativa: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={
        "px-4 py-1.5 rounded-chip text-sm font-semibold transition-colors " +
        (ativa ? "bg-surface text-primary shadow-clay-sm" : "text-text-muted")
      }
    >
      {children}
    </button>
  );
}
