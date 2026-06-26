import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button, Card, Skeleton, StatCard } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { useAuth } from "../../auth/AuthContext";
import { listarSimuladosDisponiveis } from "../../lib/api/simulados";
import { t } from "../../i18n/pt-BR";

// B1 — Início do aluno: saudação + KPIs + simulados disponíveis (GET /simulados/disponiveis).
export function AlunoInicioPage() {
  const { usuario } = useAuth();
  const query = useQuery({
    queryKey: ["aluno", "simulados"],
    queryFn: listarSimuladosDisponiveis,
  });
  const todos = query.data?.dados ?? [];
  const disponiveis = todos.filter((s) => s.status === "liberado");
  const finalizados = todos.filter((s) => s.status === "finalizado");

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-text">{t.aluno.ola(usuario?.nome ?? "")}</h1>
        <p className="text-text-muted mt-0.5">{t.aluno.subtitulo}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard
          cor="primary"
          rotulo={t.aluno.kpiDisponiveis}
          icone={<Icon name="simulados" />}
          valor={disponiveis.length}
          carregando={query.isLoading}
        />
        <StatCard
          cor="success"
          rotulo={t.aluno.kpiFinalizados}
          icone={<Icon name="check" />}
          valor={finalizados.length}
          carregando={query.isLoading}
        />
      </div>

      <section>
        <h2 className="text-lg font-bold text-text mb-3">{t.aluno.disponiveis}</h2>
        {query.isLoading ? (
          <Card>
            <Skeleton className="h-12 w-full" />
          </Card>
        ) : query.isError ? (
          <Card>
            <p className="text-danger">{t.aluno.erro}</p>
          </Card>
        ) : disponiveis.length === 0 ? (
          <Card>
            <p className="text-text-muted text-center py-6">{t.aluno.semDisponiveis}</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {disponiveis.map((s) => (
              <Card key={s.id} className="flex flex-wrap items-center gap-3">
                <div className="min-w-0">
                  <p className="font-display font-semibold text-text truncate">{s.titulo}</p>
                  <p className="text-xs text-text-muted mt-0.5">
                    {s.total_questoes} {t.aluno.questoes}
                  </p>
                </div>
                <Link to={`/app/simulados/${s.id}/responder`} state={{ titulo: s.titulo }} className="ml-auto">
                  <Button variante="primary" tamanho="sm">
                    {t.aluno.responder}
                  </Button>
                </Link>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
