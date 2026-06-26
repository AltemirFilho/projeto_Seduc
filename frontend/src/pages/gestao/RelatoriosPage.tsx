import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { Button, Card, Select, Skeleton, StatCard } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { baixarRelatorioTurma, relatorioTurma } from "../../lib/api/relatorios";
import { listarTurmas } from "../../lib/api/turmas";
import { t } from "../../i18n/pt-BR";

// C13 — Relatórios. Seletor de turma → desempenho + ranking de conteúdos + export CSV/PDF.
export function RelatoriosPage() {
  // Atalho da C11 (Turma detalhe) pode pré-selecionar a turma via ?turma=ID.
  const [searchParams] = useSearchParams();
  const [turmaId, setTurmaId] = useState(searchParams.get("turma") ?? "");
  const [exportando, setExportando] = useState<"csv" | "pdf" | null>(null);

  const turmas = useQuery({ queryKey: ["turmas"], queryFn: listarTurmas });
  const rel = useQuery({
    queryKey: ["relatorio", turmaId],
    enabled: turmaId !== "",
    queryFn: () => relatorioTurma(Number(turmaId)),
  });

  const maxTaxa = Math.max(0.01, ...(rel.data?.conteudos.map((c) => c.taxa_erro) ?? [0.01]));

  async function exportar(formato: "csv" | "pdf") {
    if (!turmaId) return;
    setExportando(formato);
    try {
      await baixarRelatorioTurma(Number(turmaId), formato);
    } catch {
      /* download falhou — silencioso por ora */
    } finally {
      setExportando(null);
    }
  }

  return (
    <div className="space-y-5 max-w-4xl">
      <h1 className="text-2xl font-bold text-text">{t.relatorios.titulo}</h1>

      <Card className="p-4">
        <label htmlFor="turma" className="text-sm font-semibold text-text">
          {t.relatorios.turma}
        </label>
        <div className="mt-1.5 max-w-xs">
          <Select id="turma" value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
            <option value="">{t.relatorios.selecioneTurma}</option>
            {turmas.data?.map((tm) => (
              <option key={tm.id} value={tm.id}>
                {tm.nome} — {tm.serie}
              </option>
            ))}
          </Select>
        </div>
      </Card>

      {turmaId === "" ? (
        <Card>
          <p className="text-text-muted text-center py-6">{t.relatorios.escolhaTurma}</p>
        </Card>
      ) : rel.isLoading ? (
        <Card className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-32 w-full" />
        </Card>
      ) : rel.isError ? (
        <Card>
          <p className="text-danger">{t.relatorios.erro}</p>
        </Card>
      ) : rel.data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard cor="secondary" rotulo={t.relatorios.kpiAlunos} icone={<Icon name="usuarios" />} valor={rel.data.alunos} />
            <StatCard cor="primary" rotulo={t.relatorios.kpiSimulados} icone={<Icon name="simulados" />} valor={rel.data.simulados_corrigidos} />
            <StatCard cor="accent" rotulo={t.relatorios.kpiMedia} icone={<Icon name="relatorios" />} valor={rel.data.media_turma.toFixed(1)} />
          </div>

          <div className="flex flex-wrap gap-2">
            <Button variante="secondary" tamanho="sm" carregando={exportando === "csv"} onClick={() => exportar("csv")}>
              {t.relatorios.exportarCsv}
            </Button>
            <Button variante="secondary" tamanho="sm" carregando={exportando === "pdf"} onClick={() => exportar("pdf")}>
              {t.relatorios.exportarPdf}
            </Button>
            <Link to="/gestao/ia/diagnostico">
              <Button variante="ghost" tamanho="sm">
                <Icon name="diagnostico" className="h-4 w-4" />
                {t.relatorios.diagnostico}
              </Button>
            </Link>
          </div>

          <Card>
            <h2 className="text-lg font-bold text-text">{t.relatorios.conteudosTitulo}</h2>
            <p className="text-sm text-text-muted mb-4">{t.relatorios.conteudosSub}</p>
            {rel.data.conteudos.length === 0 ? (
              <p className="text-text-muted text-sm">{t.relatorios.semConteudos}</p>
            ) : (
              <ul className="space-y-3">
                {rel.data.conteudos.map((c) => (
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
    </div>
  );
}
