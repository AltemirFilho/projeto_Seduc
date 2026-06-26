import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Button, Card, RiscoBadge, Skeleton, StatCard } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { riscoDoAluno } from "../../lib/api/ia";
import { relatorioTurma } from "../../lib/api/relatorios";
import { listarTurmas } from "../../lib/api/turmas";
import { listarUsuarios } from "../../lib/api/usuarios";
import type { Usuario } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// C11 — Turma (detalhe). Sem GET /turmas/{id}: a meta da turma vem do item da lista /turmas.
// Desempenho via /relatorios/turma/{id}; alunos via /usuarios?turma_id; risco por aluno sob demanda.
export function TurmaDetalhePage() {
  const { id } = useParams();
  const turmaId = Number(id);
  const [calcularRisco, setCalcularRisco] = useState(false);

  const turmas = useQuery({ queryKey: ["turmas"], queryFn: listarTurmas });
  const turma = turmas.data?.find((tm) => tm.id === turmaId);

  const rel = useQuery({
    queryKey: ["relatorio", turmaId],
    enabled: Number.isFinite(turmaId),
    queryFn: () => relatorioTurma(turmaId),
  });

  const alunosQuery = useQuery({
    queryKey: ["usuarios", turmaId, "aluno"],
    enabled: Number.isFinite(turmaId),
    queryFn: () => listarUsuarios({ turma_id: turmaId, perfil: "aluno" }),
  });
  const alunos = alunosQuery.data?.dados ?? [];

  // Top 3 conteúdos por taxa de erro (o backend já devolve o pior primeiro).
  const piores = rel.data?.conteudos.slice(0, 3) ?? [];
  const maxTaxa = Math.max(0.01, ...piores.map((c) => c.taxa_erro));

  if (turmas.isLoading) {
    return (
      <div className="space-y-5 max-w-4xl">
        <Skeleton className="h-8 w-48" />
        <Card>
          <Skeleton className="h-24 w-full" />
        </Card>
      </div>
    );
  }

  if (!turma) {
    return (
      <div className="space-y-5 max-w-4xl">
        <Card className="text-center py-10 space-y-4">
          <p className="text-text-muted">{t.turmaDetalhe.naoEncontrada}</p>
          <Link to="/gestao/turmas" className="text-primary font-semibold hover:underline">
            {t.turmaDetalhe.voltarLista}
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-5 max-w-4xl">
      {/* Cabeçalho da turma */}
      <div className="space-y-1">
        <Link
          to="/gestao/turmas"
          className="inline-flex items-center gap-1 text-sm text-text-muted hover:text-text"
        >
          <Icon name="turmas" className="h-4 w-4" />
          {t.turmaDetalhe.voltar}
        </Link>
        <h1 className="text-2xl font-bold text-text">{turma.nome}</h1>
        <p className="text-text-muted">
          {t.turmaDetalhe.serieEscola(turma.serie, turma.escola)} · {t.turmaDetalhe.ano(turma.ano_letivo)}
        </p>
      </div>

      {/* Atalhos */}
      <div className="flex flex-wrap gap-2">
        <Link to={`/gestao/relatorios?turma=${turma.id}`}>
          <Button variante="secondary" tamanho="sm">
            <Icon name="relatorios" className="h-4 w-4" />
            {t.turmaDetalhe.relatorioCompleto}
          </Button>
        </Link>
        <Link to="/gestao/ia/diagnostico">
          <Button variante="ghost" tamanho="sm">
            <Icon name="diagnostico" className="h-4 w-4" />
            {t.turmaDetalhe.diagnostico}
          </Button>
        </Link>
      </div>

      {/* KPIs de desempenho + pontos de atenção */}
      {rel.isLoading ? (
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <Skeleton className="h-12 w-full" />
            </Card>
          ))}
        </div>
      ) : rel.isError ? (
        <Card>
          <p className="text-danger">{t.turmaDetalhe.erroRelatorio}</p>
        </Card>
      ) : rel.data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard cor="secondary" rotulo={t.turmaDetalhe.kpiAlunos} icone={<Icon name="usuarios" />} valor={rel.data.alunos} />
            <StatCard cor="primary" rotulo={t.turmaDetalhe.kpiSimulados} icone={<Icon name="simulados" />} valor={rel.data.simulados_corrigidos} />
            <StatCard cor="accent" rotulo={t.turmaDetalhe.kpiMedia} icone={<Icon name="relatorios" />} valor={rel.data.media_turma.toFixed(1)} />
          </div>

          <Card>
            <h2 className="text-lg font-bold text-text">{t.turmaDetalhe.pontosAtencao}</h2>
            <p className="text-sm text-text-muted mb-4">{t.turmaDetalhe.pontosAtencaoSub}</p>
            {piores.length === 0 ? (
              <p className="text-text-muted text-sm">{t.turmaDetalhe.semPontos}</p>
            ) : (
              <ul className="space-y-3">
                {piores.map((c) => (
                  <li key={c.conteudo}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-text font-medium truncate">{c.conteudo}</span>
                      <span className="text-text-muted tabular-nums">
                        {Math.round(c.taxa_erro * 100)}% · {c.erros}/{c.total}
                      </span>
                    </div>
                    <div className="h-2.5 rounded-chip bg-surface-sunken overflow-hidden">
                      <div className="h-full rounded-chip bg-danger" style={{ width: `${(c.taxa_erro / maxTaxa) * 100}%` }} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </>
      ) : null}

      {/* Alunos da turma */}
      <Card className="p-0 overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 p-5">
          <h2 className="text-lg font-bold text-text">{t.turmaDetalhe.alunosTitulo}</h2>
          {!calcularRisco && alunos.length > 0 && (
            <Button variante="secondary" tamanho="sm" onClick={() => setCalcularRisco(true)}>
              <Icon name="risco" className="h-4 w-4" />
              {t.turmaDetalhe.calcularRisco}
            </Button>
          )}
        </div>

        {alunosQuery.isLoading ? (
          <div className="px-5 pb-5 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : alunosQuery.isError ? (
          <p className="text-danger px-5 pb-5">{t.turmaDetalhe.erroAlunos}</p>
        ) : alunos.length === 0 ? (
          <p className="text-text-muted text-center py-8">{t.turmaDetalhe.semAlunos}</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-text-muted">
                  <th className="px-5 py-3 font-semibold">{t.turmaDetalhe.colNome}</th>
                  <th className="px-3 py-3 font-semibold">{t.turmaDetalhe.colEmail}</th>
                  <th className="px-3 py-3 font-semibold">{t.turmaDetalhe.colRisco}</th>
                  <th className="px-5 py-3 font-semibold text-right">{t.turmaDetalhe.colAcoes}</th>
                </tr>
              </thead>
              <tbody>
                {alunos.map((aluno) => (
                  <LinhaAluno key={aluno.id} aluno={aluno} calcular={calcularRisco} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}

// Linha de aluno — o risco só é calculado (e salvo no backend) quando `calcular` vira true.
function LinhaAluno({ aluno, calcular }: { aluno: Usuario; calcular: boolean }) {
  // /ia/risco usa o id da entidade Aluno (aluno_id), que difere do usuario.id.
  const alunoId = aluno.aluno_id;
  const risco = useQuery({
    queryKey: ["risco", alunoId],
    enabled: calcular && alunoId != null,
    queryFn: () => riscoDoAluno(alunoId as number),
  });

  return (
    <tr className="border-t border-line">
      <td className="px-5 py-3 text-text whitespace-nowrap">{aluno.nome}</td>
      <td className="px-3 py-3 text-text-muted">{aluno.email}</td>
      <td className="px-3 py-3">
        {!calcular ? (
          <span className="text-text-muted">{t.turmaDetalhe.riscoPendente}</span>
        ) : risco.isLoading ? (
          <Skeleton className="h-6 w-28" />
        ) : risco.isError ? (
          <span className="text-danger text-xs">{t.turmaDetalhe.riscoErro}</span>
        ) : risco.data ? (
          <RiscoBadge classificacao={risco.data.classificacao} score={risco.data.score_risco} />
        ) : null}
      </td>
      <td className="px-5 py-3 text-right">
        {alunoId != null && (
          <Link to={`/gestao/ia/risco/${alunoId}`} className="text-primary font-semibold hover:underline">
            {t.turmaDetalhe.verRisco}
          </Link>
        )}
      </td>
    </tr>
  );
}
