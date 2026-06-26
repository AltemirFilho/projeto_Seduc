import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Card, Skeleton, StatCard } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { listarTurmas } from "../../lib/api/turmas";
import { t } from "../../i18n/pt-BR";

// C10 — Turmas. GET /turmas (lista flat). Sem GET /turmas/{id}: detalhe via relatório.
export function TurmasPage() {
  const query = useQuery({ queryKey: ["turmas"], queryFn: listarTurmas });
  const turmas = query.data ?? [];

  return (
    <div className="space-y-5 max-w-4xl">
      <h1 className="text-2xl font-bold text-text">{t.turmasGestao.titulo}</h1>

      {query.isLoading ? (
        <Card>
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        </Card>
      ) : query.isError ? (
        <Card>
          <p className="text-danger">{t.turmasGestao.erro}</p>
        </Card>
      ) : (
        <>
          <div className="max-w-xs">
            <StatCard cor="primary" rotulo={t.turmasGestao.kpiTurmas} icone={<Icon name="turmas" />} valor={turmas.length} />
          </div>

          {turmas.length === 0 ? (
            <Card>
              <p className="text-text-muted text-center py-6">{t.turmasGestao.vazio}</p>
            </Card>
          ) : (
            <Card className="p-0 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-text-muted">
                      <th className="px-5 py-3 font-semibold">{t.turmasGestao.colNome}</th>
                      <th className="px-3 py-3 font-semibold">{t.turmasGestao.colSerie}</th>
                      <th className="px-3 py-3 font-semibold">{t.turmasGestao.colEscola}</th>
                      <th className="px-3 py-3 font-semibold">{t.turmasGestao.colAno}</th>
                      <th className="px-5 py-3 font-semibold text-right">{t.questoes.colAcoes}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {turmas.map((tm) => (
                      <tr key={tm.id} className="border-t border-line">
                        <td className="px-5 py-3 whitespace-nowrap">
                          <Link
                            to={`/gestao/turmas/${tm.id}`}
                            className="text-text font-medium hover:text-primary hover:underline"
                          >
                            {tm.nome}
                          </Link>
                        </td>
                        <td className="px-3 py-3 text-text-muted whitespace-nowrap">{tm.serie}</td>
                        <td className="px-3 py-3 text-text-muted">{tm.escola}</td>
                        <td className="px-3 py-3 text-text-muted tabular-nums">{tm.ano_letivo}</td>
                        <td className="px-5 py-3 text-right">
                          <Link to={`/gestao/turmas/${tm.id}`} className="text-primary font-semibold hover:underline">
                            {t.turmasGestao.abrir}
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
