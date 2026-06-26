import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Card, Skeleton, StatCard } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { useAuth } from "../../auth/AuthContext";
import { listarMaterias } from "../../lib/api/etiquetas";
import { contarQuestoes, listarQuestoes } from "../../lib/api/questoes";
import { listarTurmas } from "../../lib/api/turmas";
import { listarUsuarios } from "../../lib/api/usuarios";
import { t } from "../../i18n/pt-BR";

// C1 — Dashboard da gestão. Dados reais onde o backend expõe; gaps marcados "exemplo".
export function DashboardPage() {
  const { usuario } = useAuth();

  const questoes = useQuery({
    queryKey: ["questoes", "total"],
    queryFn: () => listarQuestoes({ por_pagina: 1 }),
  });
  const turmas = useQuery({ queryKey: ["turmas"], queryFn: listarTurmas });
  const materias = useQuery({ queryKey: ["etiquetas", "materias"], queryFn: listarMaterias });
  const alunos = useQuery({
    queryKey: ["usuarios", "alunos", "total"],
    queryFn: () => listarUsuarios({ perfil: "aluno" }),
  });

  // Distribuição real: total de questões por matéria (uma contagem por matéria).
  const distribuicao = useQuery({
    queryKey: ["questoes", "por-materia", materias.data?.map((m) => m.nome)],
    enabled: !!materias.data && materias.data.length > 0,
    queryFn: async () => {
      const lista = materias.data!;
      const totais = await Promise.all(lista.map((m) => contarQuestoes({ materia: m.nome })));
      return lista
        .map((m, i) => ({ materia: m.nome, total: totais[i] }))
        .sort((a, b) => b.total - a.total);
    },
  });

  const maxDist = Math.max(1, ...(distribuicao.data?.map((d) => d.total) ?? [1]));

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold text-text">{t.dashboard.titulo}</h1>
        <p className="text-text-muted mt-0.5">{t.dashboard.saudacao(usuario?.nome ?? "")}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          cor="primary"
          rotulo={t.dashboard.kpiQuestoes}
          icone={<Icon name="banco" />}
          carregando={questoes.isLoading}
          valor={questoes.isError ? "—" : questoes.data?.meta.total ?? "—"}
        />
        {/* gap: não há GET /simulados */}
        <StatCard cor="accent" rotulo={t.dashboard.kpiSimulados} icone={<Icon name="simulados" />} valor="—" exemplo />
        <StatCard
          cor="secondary"
          rotulo={t.dashboard.kpiTurmas}
          icone={<Icon name="turmas" />}
          carregando={turmas.isLoading}
          valor={turmas.isError ? "—" : turmas.data?.length ?? "—"}
        />
        <StatCard
          cor="success"
          rotulo={t.dashboard.kpiAlunos}
          icone={<Icon name="usuarios" />}
          carregando={alunos.isLoading}
          valor={alunos.isError ? "—" : alunos.data?.meta.total ?? "—"}
        />
      </div>

      <section>
        <h2 className="text-lg font-bold text-text mb-3">{t.dashboard.acoesRapidas}</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          <AcaoRapida to="/gestao/questoes/nova" icone="banco" titulo={t.dashboard.novaQuestao} />
          <AcaoRapida to="/gestao/simulados/novo" icone="simulados" titulo={t.dashboard.novoSimulado} />
          <AcaoRapida to="/gestao/usuarios" icone="usuarios" titulo={t.dashboard.cadastrarUsuario} />
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="text-lg font-bold text-text">{t.dashboard.distribuicaoTitulo}</h2>
          <p className="text-sm text-text-muted mb-4">{t.dashboard.distribuicaoSub}</p>

          {materias.isLoading || distribuicao.isLoading ? (
            <div className="space-y-3">
              {[0, 1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-6 w-full" />
              ))}
            </div>
          ) : materias.isError || distribuicao.isError ? (
            <p className="text-danger text-sm">{t.dashboard.erroDados}</p>
          ) : (distribuicao.data?.length ?? 0) === 0 ? (
            <p className="text-text-muted text-sm">{t.dashboard.semDados}</p>
          ) : (
            <ul className="space-y-3">
              {distribuicao.data!.map((d) => (
                <li key={d.materia}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-text font-medium truncate">{d.materia}</span>
                    <span className="text-text-muted tabular-nums">{d.total}</span>
                  </div>
                  <div className="h-2.5 rounded-chip bg-surface-sunken overflow-hidden">
                    <div
                      className="h-full rounded-chip bg-primary"
                      style={{ width: `${(d.total / maxDist) * 100}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <h2 className="text-lg font-bold text-text">{t.dashboard.alertasTitulo}</h2>
          <p className="text-sm text-text-muted mb-4">{t.dashboard.alertasSub}</p>
          <div className="rounded-2xl bg-surface-sunken p-6 text-center">
            <div className="mx-auto grid place-items-center h-12 w-12 rounded-full bg-accent/15 text-accent-ink mb-3">
              <Icon name="risco" />
            </div>
            <p className="text-sm text-text-muted">{t.dashboard.alertasGap}</p>
          </div>
        </Card>
      </div>
    </div>
  );
}

function AcaoRapida({ to, icone, titulo }: { to: string; icone: string; titulo: string }) {
  return (
    <Link
      to={to}
      className="group flex items-center gap-3 bg-surface rounded-card shadow-clay-sm p-4 transition-transform hover:-translate-y-0.5"
    >
      <span className="grid place-items-center h-10 w-10 rounded-2xl bg-primary text-on-primary shadow-clay-sm shrink-0">
        <Icon name={icone} className="h-5 w-5" />
      </span>
      <span className="font-display font-semibold text-text">{titulo}</span>
    </Link>
  );
}
