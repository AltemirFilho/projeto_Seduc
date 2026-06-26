import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Button, Card, Select, Skeleton } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import {
  listarConteudos,
  listarMaterias,
  listarNiveis,
  listarSeries,
} from "../../lib/api/etiquetas";
import { listarQuestoes } from "../../lib/api/questoes";
import { t } from "../../i18n/pt-BR";

const POR_PAGINA = 10;

// C2 — Banco de questões. FiltroBar (etiquetas reais) + DataTable paginada (envelope {dados,meta}).
export function QuestoesPage() {
  const [serie, setSerie] = useState("");
  const [materia, setMateria] = useState("");
  const [conteudo, setConteudo] = useState("");
  const [nivel, setNivel] = useState("");
  const [pagina, setPagina] = useState(1);

  const series = useQuery({ queryKey: ["etiquetas", "series"], queryFn: listarSeries });
  const materias = useQuery({ queryKey: ["etiquetas", "materias"], queryFn: listarMaterias });
  const niveis = useQuery({ queryKey: ["etiquetas", "niveis"], queryFn: listarNiveis });
  const conteudos = useQuery({
    queryKey: ["etiquetas", "conteudos", materia],
    queryFn: () => listarConteudos(materia || undefined),
  });

  const questoes = useQuery({
    queryKey: ["questoes", "lista", { serie, materia, conteudo, nivel, pagina }],
    queryFn: () =>
      listarQuestoes({
        serie: serie || undefined,
        materia: materia || undefined,
        conteudo: conteudo || undefined,
        nivel: nivel || undefined,
        pagina,
        por_pagina: POR_PAGINA,
      }),
    placeholderData: keepPreviousData,
  });

  function aplicar(setter: (v: string) => void, valor: string) {
    setter(valor);
    setPagina(1);
  }
  function aoMudarMateria(valor: string) {
    setMateria(valor);
    setConteudo(""); // conteúdos dependem da matéria
    setPagina(1);
  }
  function limpar() {
    setSerie("");
    setMateria("");
    setConteudo("");
    setNivel("");
    setPagina(1);
  }

  const dados = questoes.data?.dados ?? [];
  const meta = questoes.data?.meta;
  const temFiltro = Boolean(serie || materia || conteudo || nivel);

  return (
    <div className="space-y-5 max-w-6xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-text">{t.questoes.titulo}</h1>
          {meta && <p className="text-sm text-text-muted mt-0.5">{t.questoes.total(meta.total)}</p>}
        </div>
        <div className="flex gap-2">
          <Link to="/gestao/importar">
            <Button variante="secondary" tamanho="sm">
              <Icon name="importar" className="h-4 w-4" />
              {t.questoes.importar}
            </Button>
          </Link>
          <Link to="/gestao/questoes/nova">
            <Button variante="primary" tamanho="sm">
              <Icon name="banco" className="h-4 w-4" />
              {t.questoes.novaQuestao}
            </Button>
          </Link>
        </div>
      </div>

      <Card className="p-4">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Select value={serie} aria-label={t.novaQuestao.serie} onChange={(e) => aplicar(setSerie, e.target.value)}>
            <option value="">{t.questoes.todasSeries}</option>
            {series.data?.map((s) => (
              <option key={s.id} value={s.nome}>
                {s.nome}
              </option>
            ))}
          </Select>
          <Select value={materia} aria-label={t.novaQuestao.materia} onChange={(e) => aoMudarMateria(e.target.value)}>
            <option value="">{t.questoes.todasMaterias}</option>
            {materias.data?.map((m) => (
              <option key={m.id} value={m.nome}>
                {m.nome}
              </option>
            ))}
          </Select>
          <Select value={conteudo} aria-label={t.novaQuestao.conteudo} onChange={(e) => aplicar(setConteudo, e.target.value)}>
            <option value="">{t.questoes.todosConteudos}</option>
            {conteudos.data?.map((c) => (
              <option key={c.id} value={c.nome}>
                {c.nome}
              </option>
            ))}
          </Select>
          <Select value={nivel} aria-label={t.novaQuestao.nivel} onChange={(e) => aplicar(setNivel, e.target.value)}>
            <option value="">{t.questoes.todosNiveis}</option>
            {niveis.data?.map((n) => (
              <option key={n.id} value={n.nome}>
                {n.nome}
              </option>
            ))}
          </Select>
        </div>
        {temFiltro && (
          <div className="mt-3">
            <Button variante="ghost" tamanho="sm" onClick={limpar}>
              {t.questoes.limparFiltros}
            </Button>
          </div>
        )}
      </Card>

      {questoes.isLoading ? (
        <Card>
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </Card>
      ) : questoes.isError ? (
        <Card>
          <p className="text-danger">{t.questoes.erro}</p>
        </Card>
      ) : dados.length === 0 ? (
        <Card>
          <p className="text-text-muted text-center py-6">{t.questoes.vazio}</p>
        </Card>
      ) : (
        <>
          {/* Tabela (sm+) */}
          <Card className="hidden sm:block p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-text-muted">
                  <th className="px-5 py-3 font-semibold">{t.questoes.colEnunciado}</th>
                  <th className="px-3 py-3 font-semibold">{t.questoes.colMateria}</th>
                  <th className="px-3 py-3 font-semibold">{t.questoes.colConteudo}</th>
                  <th className="px-3 py-3 font-semibold">{t.questoes.colNivel}</th>
                  <th className="px-3 py-3 font-semibold text-center">{t.questoes.colAlternativas}</th>
                  <th className="px-5 py-3 font-semibold text-right">{t.questoes.colAcoes}</th>
                </tr>
              </thead>
              <tbody>
                {dados.map((q) => (
                  <tr key={q.id} className="border-t border-line hover:bg-surface-sunken/50 transition-colors">
                    <td className="px-5 py-3 text-text max-w-[360px]">
                      <span className="line-clamp-2">{q.enunciado}</span>
                    </td>
                    <td className="px-3 py-3 text-text-muted whitespace-nowrap">{q.materia}</td>
                    <td className="px-3 py-3 text-text-muted whitespace-nowrap">{q.conteudo}</td>
                    <td className="px-3 py-3">
                      <NivelChip nivel={q.nivel} />
                    </td>
                    <td className="px-3 py-3 text-center text-text-muted tabular-nums">{q.alternativas.length}</td>
                    <td className="px-5 py-3 text-right">
                      <Link
                        to={`/gestao/questoes/${q.id}`}
                        state={{ questao: q }}
                        className="text-primary font-semibold hover:underline"
                      >
                        {t.questoes.ver}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Cards (mobile) */}
          <div className="sm:hidden space-y-3">
            {dados.map((q) => (
              <Card key={q.id} className="p-4">
                <p className="text-text line-clamp-3">{q.enunciado}</p>
                <div className="flex flex-wrap items-center gap-2 mt-3 text-xs text-text-muted">
                  <span>{q.materia}</span>
                  <span aria-hidden="true">·</span>
                  <span>{q.conteudo}</span>
                  <NivelChip nivel={q.nivel} />
                  <span className="ml-auto">{q.alternativas.length} alt.</span>
                </div>
                <div className="mt-3">
                  <Link
                    to={`/gestao/questoes/${q.id}`}
                    state={{ questao: q }}
                    className="text-primary font-semibold text-sm hover:underline"
                  >
                    {t.questoes.ver}
                  </Link>
                </div>
              </Card>
            ))}
          </div>

          {meta && meta.totalPaginas > 1 && (
            <div className="flex items-center justify-between gap-3">
              <Button variante="secondary" tamanho="sm" disabled={pagina <= 1} onClick={() => setPagina((p) => Math.max(1, p - 1))}>
                {t.questoes.anterior}
              </Button>
              <span className="text-sm text-text-muted">{t.questoes.paginaInfo(meta.pagina, meta.totalPaginas)}</span>
              <Button
                variante="secondary"
                tamanho="sm"
                disabled={pagina >= meta.totalPaginas}
                onClick={() => setPagina((p) => p + 1)}
              >
                {t.questoes.proxima}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function NivelChip({ nivel }: { nivel: string }) {
  return (
    <span className="inline-block px-2 py-0.5 rounded-chip bg-secondary/40 text-secondary-ink text-xs font-medium whitespace-nowrap">
      {nivel}
    </span>
  );
}
