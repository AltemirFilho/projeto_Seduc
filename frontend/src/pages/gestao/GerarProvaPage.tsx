import { useMutation, useQuery } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { Button, Card, Field, Input } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { ApiError } from "../../lib/api/client";
import { listarMaterias, listarSeries } from "../../lib/api/etiquetas";
import { gerarProva } from "../../lib/api/provas";
import type { GerarProvaParams } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// C5 — Gerar prova avulsa. POST /provas/gerar → prévia com questões + gabarito + distribuição real.
export function GerarProvaPage() {
  const [serie, setSerie] = useState("");
  const [materia, setMateria] = useState("");
  const [quantidade, setQuantidade] = useState(10);
  const [facil, setFacil] = useState("");
  const [medio, setMedio] = useState("");
  const [dificil, setDificil] = useState("");
  const [seed, setSeed] = useState("");
  const [erroValidacao, setErroValidacao] = useState<string | null>(null);

  const series = useQuery({ queryKey: ["etiquetas", "series"], queryFn: listarSeries });
  const materias = useQuery({ queryKey: ["etiquetas", "materias"], queryFn: listarMaterias });

  const mutation = useMutation({ mutationFn: (p: GerarProvaParams) => gerarProva(p) });

  function montarDistribuicao(): Record<string, number> | undefined {
    const f = Number(facil) || 0;
    const m = Number(medio) || 0;
    const d = Number(dificil) || 0;
    const soma = f + m + d;
    if (soma <= 0) return undefined;
    return { Fácil: f / soma, Médio: m / soma, Difícil: d / soma };
  }

  function montarParams(): GerarProvaParams {
    return {
      serie: serie.trim(),
      materia: materia.trim(),
      quantidade,
      distribuicao: montarDistribuicao(),
      seed: seed.trim() ? Number(seed) : undefined,
    };
  }

  function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    if (!serie.trim() || !materia.trim()) {
      setErroValidacao(t.gerarProva.erroCampos);
      return;
    }
    setErroValidacao(null);
    mutation.mutate(montarParams());
  }

  const erroServidor = mutation.error
    ? mutation.error instanceof ApiError
      ? mutation.error.message || t.gerarProva.erro
      : t.gerarProva.erro
    : null;
  const erro = erroValidacao ?? erroServidor;
  const prova = mutation.data;

  return (
    <div className="space-y-5 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-text">{t.gerarProva.titulo}</h1>
        <p className="text-text-muted mt-0.5">{t.gerarProva.sub}</p>
      </div>

      <form onSubmit={onSubmit} noValidate>
        <Card className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label={t.gerarProva.serie} htmlFor="serie">
              <Input id="serie" list="lst-series" value={serie} onChange={(e) => setSerie(e.target.value)} />
              <datalist id="lst-series">{series.data?.map((s) => <option key={s.id} value={s.nome} />)}</datalist>
            </Field>
            <Field label={t.gerarProva.materia} htmlFor="materia">
              <Input id="materia" list="lst-materias" value={materia} onChange={(e) => setMateria(e.target.value)} />
              <datalist id="lst-materias">{materias.data?.map((m) => <option key={m.id} value={m.nome} />)}</datalist>
            </Field>
            <Field label={t.gerarProva.quantidade} htmlFor="qtd">
              <Input
                id="qtd"
                type="number"
                min={1}
                max={100}
                value={quantidade}
                onChange={(e) => setQuantidade(Math.max(1, Math.min(100, Number(e.target.value) || 1)))}
              />
            </Field>
            <Field label={t.gerarProva.seed} htmlFor="seed">
              <Input id="seed" type="number" value={seed} onChange={(e) => setSeed(e.target.value)} placeholder="—" />
            </Field>
          </div>

          <div>
            <p className="text-sm font-semibold text-text">{t.gerarProva.distribuicao}</p>
            <p className="text-xs text-text-muted mb-2">{t.gerarProva.distribuicaoDica}</p>
            <div className="grid grid-cols-3 gap-3 max-w-md">
              <Field label={t.gerarProva.facil} htmlFor="f">
                <Input id="f" type="number" min={0} max={100} value={facil} onChange={(e) => setFacil(e.target.value)} placeholder="0" />
              </Field>
              <Field label={t.gerarProva.medio} htmlFor="m">
                <Input id="m" type="number" min={0} max={100} value={medio} onChange={(e) => setMedio(e.target.value)} placeholder="0" />
              </Field>
              <Field label={t.gerarProva.dificil} htmlFor="d">
                <Input id="d" type="number" min={0} max={100} value={dificil} onChange={(e) => setDificil(e.target.value)} placeholder="0" />
              </Field>
            </div>
          </div>

          {erro && (
            <p role="alert" className="text-danger text-sm">
              {erro}
            </p>
          )}

          <Button type="submit" variante="primary" carregando={mutation.isPending}>
            {mutation.isPending ? t.gerarProva.gerando : t.gerarProva.gerar}
          </Button>
        </Card>
      </form>

      {prova && (
        <>
          <Card className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-text">{t.gerarProva.resultadoTitulo}</h2>
                <p className="text-sm text-text-muted">
                  {prova.serie} · {prova.materias.join(", ")} · {t.gerarProva.total(prova.total)}
                </p>
              </div>
              <div className="flex gap-2">
                <Button variante="secondary" tamanho="sm" onClick={() => mutation.mutate(montarParams())}>
                  {t.gerarProva.regerar}
                </Button>
                <Link to="/gestao/simulados/novo">
                  <Button variante="ghost" tamanho="sm">
                    {t.gerarProva.usarSimulado}
                  </Button>
                </Link>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-text-muted">{t.gerarProva.distribReal}:</span>
              {Object.entries(prova.distribuicao_real).map(([nivel, n]) => (
                <span key={nivel} className="px-2 py-0.5 rounded-chip bg-secondary/40 text-secondary-ink text-xs font-medium">
                  {nivel}: {n}
                </span>
              ))}
            </div>
          </Card>

          <div className="space-y-3">
            {prova.questoes.map((q) => (
              <Card key={q.questao_id} className="space-y-2">
                <p className="text-xs text-text-muted">
                  {q.ordem}. {q.conteudo} · {q.nivel}
                </p>
                <p className="text-text font-medium">{q.enunciado}</p>
                <ul className="space-y-1">
                  {q.alternativas.map((alt) => {
                    const correta = prova.gabarito[String(q.ordem)] === alt.letra;
                    return (
                      <li
                        key={alt.alternativa_id}
                        className={"flex items-start gap-2 p-2 rounded-xl text-sm " + (correta ? "bg-success/10" : "")}
                      >
                        <span className={"font-semibold " + (correta ? "text-success" : "text-text-muted")}>{alt.letra}</span>
                        <span className="text-text">{alt.texto}</span>
                        {correta && <Icon name="check" className="h-4 w-4 text-success ml-auto shrink-0" />}
                      </li>
                    );
                  })}
                </ul>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
