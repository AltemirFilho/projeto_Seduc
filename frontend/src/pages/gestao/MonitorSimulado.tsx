import { useQuery } from "@tanstack/react-query";

import { Card, Skeleton, StatCard } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { monitorarSimulado } from "../../lib/api/simulados";
import type { SituacaoMonitor } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// C9 — Monitorar simulado. Progresso ao vivo da turma via GET /simulados/{id}/monitoramento
// (derivado das respostas já registradas — sem flag de "entregue" no backend).
const CORES_SIT: Record<SituacaoMonitor, { bg: string; cor: string }> = {
  concluido: { bg: "rgba(79,157,107,0.18)", cor: "#2c6243" },
  em_andamento: { bg: "rgba(94,134,194,0.18)", cor: "#274c84" },
  nao_iniciou: { bg: "rgba(154,146,126,0.18)", cor: "#5c5341" },
};

export function MonitorSimulado({ simuladoId }: { simuladoId: number }) {
  const query = useQuery({
    queryKey: ["simulado", "monitor", simuladoId],
    queryFn: () => monitorarSimulado(simuladoId),
  });

  if (query.isLoading) {
    return (
      <Card className="space-y-3">
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-32 w-full" />
      </Card>
    );
  }
  if (query.isError || !query.data) {
    return (
      <Card>
        <p className="text-danger">{t.monitor.erro}</p>
      </Card>
    );
  }

  const mon = query.data;
  const pct = mon.total_alunos
    ? Math.round((mon.concluidos / mon.total_alunos) * 100)
    : 0;

  return (
    <div className="space-y-5">
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <StatCard cor="success" icone={<Icon name="check" />} rotulo={t.monitor.kpiConcluido} valor={mon.concluidos} />
        <StatCard cor="secondary" icone={<Icon name="simulados" />} rotulo={t.monitor.kpiEmAndamento} valor={mon.em_andamento} />
        <StatCard cor="primary" icone={<Icon name="usuarios" />} rotulo={t.monitor.kpiNaoIniciou} valor={mon.nao_iniciaram} />
        <StatCard cor="accent" icone={<Icon name="relatorios" />} rotulo={t.monitor.kpiAlunos} valor={mon.total_alunos} />
      </div>

      <Card>
        <div className="flex justify-between text-sm mb-1.5">
          <span className="font-display font-bold text-text">{t.monitor.progressoGeralTitulo}</span>
          <span className="text-text-muted tabular-nums">
            {t.monitor.progressoGeral(mon.concluidos, mon.total_alunos)}
          </span>
        </div>
        <div className="h-3 rounded-chip bg-surface-sunken overflow-hidden">
          <div className="h-full rounded-chip bg-success" style={{ width: `${pct}%` }} />
        </div>
      </Card>

      <Card className="p-0 overflow-hidden">
        <h3 className="text-lg font-bold text-text p-5 pb-3">{t.monitor.listaTitulo}</h3>
        {mon.por_aluno.length === 0 ? (
          <p className="text-text-muted text-center py-8">{t.monitor.semAlunos}</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-text-muted">
                  <th className="px-5 py-3 font-semibold">{t.monitor.colAluno}</th>
                  <th className="px-3 py-3 font-semibold">{t.monitor.colSituacao}</th>
                  <th className="px-5 py-3 font-semibold">{t.monitor.colProgresso}</th>
                </tr>
              </thead>
              <tbody>
                {mon.por_aluno.map((a) => {
                  const c = CORES_SIT[a.situacao];
                  const p = a.total ? (a.respondidas / a.total) * 100 : 0;
                  return (
                    <tr key={a.aluno_id} className="border-t border-line">
                      <td className="px-5 py-3 text-text whitespace-nowrap">{a.nome}</td>
                      <td className="px-3 py-3">
                        <span
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-chip text-xs font-semibold"
                          style={{ backgroundColor: c.bg, color: c.cor }}
                        >
                          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: c.cor }} aria-hidden="true" />
                          {t.monitor.situacao[a.situacao]}
                        </span>
                      </td>
                      <td className="px-5 py-3 min-w-[160px]">
                        <div className="flex items-center gap-2">
                          <div className="h-2 flex-1 rounded-chip bg-surface-sunken overflow-hidden">
                            <div className="h-full rounded-chip bg-primary" style={{ width: `${p}%` }} />
                          </div>
                          <span className="text-text-muted tabular-nums text-xs">
                            {a.respondidas}/{a.total}
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
