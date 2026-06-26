import { useQuery } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import { Button, Card, Field, Input, Textarea } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import {
  listarConteudos,
  listarMaterias,
  listarNiveis,
  listarSeries,
} from "../../lib/api/etiquetas";
import type { NovaQuestao, Questao } from "../../types/api";
import { t } from "../../i18n/pt-BR";

interface AltState {
  texto: string;
  correta: boolean;
}

interface Props {
  inicial?: Questao;
  salvando: boolean;
  erroServidor?: string | null;
  textoSalvar: string;
  textoSalvando: string;
  onSubmit: (payload: NovaQuestao) => void;
  onCancelar: () => void;
}

// Formulário de questão compartilhado por C3 (criar) e C4 (editar).
export function QuestaoForm({
  inicial,
  salvando,
  erroServidor,
  textoSalvar,
  textoSalvando,
  onSubmit,
  onCancelar,
}: Props) {
  const [enunciado, setEnunciado] = useState(inicial?.enunciado ?? "");
  const [serie, setSerie] = useState(inicial?.serie ?? "");
  const [materia, setMateria] = useState(inicial?.materia ?? "");
  const [conteudo, setConteudo] = useState(inicial?.conteudo ?? "");
  const [nivel, setNivel] = useState(inicial?.nivel ?? "");
  const [alternativas, setAlternativas] = useState<AltState[]>(
    inicial?.alternativas.map((a) => ({ texto: a.texto, correta: a.correta })) ?? [
      { texto: "", correta: true },
      { texto: "", correta: false },
    ],
  );
  const [adaptacoes, setAdaptacoes] = useState<string[]>(inicial?.adaptacoes ?? []);
  const [novaAdaptacao, setNovaAdaptacao] = useState("");
  const [erroValidacao, setErroValidacao] = useState<string | null>(null);

  const series = useQuery({ queryKey: ["etiquetas", "series"], queryFn: listarSeries });
  const materias = useQuery({ queryKey: ["etiquetas", "materias"], queryFn: listarMaterias });
  const niveis = useQuery({ queryKey: ["etiquetas", "niveis"], queryFn: listarNiveis });
  const conteudos = useQuery({
    queryKey: ["etiquetas", "conteudos", materia],
    queryFn: () => listarConteudos(materia || undefined),
  });

  function patchAlt(i: number, patch: Partial<AltState>) {
    setAlternativas((prev) => prev.map((a, idx) => (idx === i ? { ...a, ...patch } : a)));
  }
  function marcarCorreta(i: number) {
    setAlternativas((prev) => prev.map((a, idx) => ({ ...a, correta: idx === i })));
  }
  function adicionarAlt() {
    setAlternativas((prev) => (prev.length >= 5 ? prev : [...prev, { texto: "", correta: false }]));
  }
  function removerAlt(i: number) {
    setAlternativas((prev) => {
      if (prev.length <= 2) return prev;
      const next = prev.filter((_, idx) => idx !== i);
      if (!next.some((a) => a.correta)) next[0] = { ...next[0], correta: true };
      return next;
    });
  }
  function adicionarAdaptacao() {
    const v = novaAdaptacao.trim();
    if (v && !adaptacoes.includes(v)) setAdaptacoes((prev) => [...prev, v]);
    setNovaAdaptacao("");
  }
  function removerAdaptacao(v: string) {
    setAdaptacoes((prev) => prev.filter((a) => a !== v));
  }

  function validar(): string | null {
    if (!enunciado.trim()) return t.novaQuestao.erroEnunciado;
    if (!serie.trim() || !materia.trim() || !conteudo.trim() || !nivel.trim())
      return t.novaQuestao.erroClassificacao;
    const preenchidas = alternativas.filter((a) => a.texto.trim());
    if (preenchidas.length < 2 || preenchidas.length !== alternativas.length)
      return t.novaQuestao.erroAlternativas;
    if (alternativas.filter((a) => a.correta).length !== 1) return t.novaQuestao.erroUmaCorreta;
    return null;
  }

  function aoEnviar(ev: FormEvent) {
    ev.preventDefault();
    const erro = validar();
    setErroValidacao(erro);
    if (erro) return;
    onSubmit({
      enunciado: enunciado.trim(),
      serie: serie.trim(),
      materia: materia.trim(),
      conteudo: conteudo.trim(),
      nivel: nivel.trim(),
      adaptacoes,
      alternativas: alternativas.map((a) => ({ texto: a.texto.trim(), correta: a.correta })),
    });
  }

  const erro = erroValidacao ?? erroServidor ?? null;

  return (
    <form onSubmit={aoEnviar} className="space-y-5" noValidate>
      <Card className="space-y-3">
        <h2 className="font-display font-bold text-text">{t.novaQuestao.secEnunciado}</h2>
        <Field label={t.novaQuestao.enunciado} htmlFor="enunciado">
          <Textarea
            id="enunciado"
            value={enunciado}
            onChange={(e) => setEnunciado(e.target.value)}
            placeholder={t.novaQuestao.enunciadoPlaceholder}
          />
        </Field>
      </Card>

      <Card className="space-y-3">
        <div>
          <h2 className="font-display font-bold text-text">{t.novaQuestao.secClassificacao}</h2>
          <p className="text-xs text-text-muted">{t.novaQuestao.dicaNovo}</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label={t.novaQuestao.serie} htmlFor="serie">
            <Input id="serie" list="lst-series" value={serie} onChange={(e) => setSerie(e.target.value)} />
            <datalist id="lst-series">{series.data?.map((s) => <option key={s.id} value={s.nome} />)}</datalist>
          </Field>
          <Field label={t.novaQuestao.nivel} htmlFor="nivel">
            <Input id="nivel" list="lst-niveis" value={nivel} onChange={(e) => setNivel(e.target.value)} />
            <datalist id="lst-niveis">{niveis.data?.map((n) => <option key={n.id} value={n.nome} />)}</datalist>
          </Field>
          <Field label={t.novaQuestao.materia} htmlFor="materia">
            <Input id="materia" list="lst-materias" value={materia} onChange={(e) => setMateria(e.target.value)} />
            <datalist id="lst-materias">{materias.data?.map((m) => <option key={m.id} value={m.nome} />)}</datalist>
          </Field>
          <Field label={t.novaQuestao.conteudo} htmlFor="conteudo">
            <Input id="conteudo" list="lst-conteudos" value={conteudo} onChange={(e) => setConteudo(e.target.value)} />
            <datalist id="lst-conteudos">{conteudos.data?.map((c) => <option key={c.id} value={c.nome} />)}</datalist>
          </Field>
        </div>
      </Card>

      <Card className="space-y-3">
        <div>
          <h2 className="font-display font-bold text-text">{t.novaQuestao.secAlternativas}</h2>
          <p className="text-xs text-text-muted">{t.novaQuestao.dicaCorreta}</p>
        </div>
        <ul className="space-y-2">
          {alternativas.map((a, i) => (
            <li key={i} className="flex items-center gap-2">
              <input
                type="radio"
                name="correta"
                checked={a.correta}
                onChange={() => marcarCorreta(i)}
                className="h-5 w-5 shrink-0 accent-[#182350] cursor-pointer"
                aria-label={`${t.novaQuestao.correta}: ${t.novaQuestao.alternativa(i + 1)}`}
              />
              <Input
                value={a.texto}
                onChange={(e) => patchAlt(i, { texto: e.target.value })}
                placeholder={t.novaQuestao.alternativa(i + 1)}
              />
              <button
                type="button"
                onClick={() => removerAlt(i)}
                disabled={alternativas.length <= 2}
                className="p-2 rounded-full text-text-muted hover:bg-surface-sunken disabled:opacity-40 disabled:pointer-events-none"
                aria-label={t.novaQuestao.removerAlternativa}
              >
                <Icon name="fechar" className="h-4 w-4" />
              </button>
            </li>
          ))}
        </ul>
        {alternativas.length < 5 && (
          <Button type="button" variante="ghost" tamanho="sm" onClick={adicionarAlt}>
            + {t.novaQuestao.adicionarAlternativa}
          </Button>
        )}
      </Card>

      <Card className="space-y-3">
        <h2 className="font-display font-bold text-text">{t.novaQuestao.secAdaptacoes}</h2>
        <div className="flex gap-2">
          <Input
            value={novaAdaptacao}
            onChange={(e) => setNovaAdaptacao(e.target.value)}
            placeholder={t.novaQuestao.adaptacaoPlaceholder}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                adicionarAdaptacao();
              }
            }}
          />
          <Button type="button" variante="secondary" onClick={adicionarAdaptacao}>
            {t.novaQuestao.adicionar}
          </Button>
        </div>
        {adaptacoes.length > 0 && (
          <ul className="flex flex-wrap gap-2">
            {adaptacoes.map((a) => (
              <li key={a} className="flex items-center gap-1.5 px-3 py-1 rounded-chip bg-accent/15 text-accent-ink text-sm">
                {a}
                <button type="button" onClick={() => removerAdaptacao(a)} aria-label={`${t.novaQuestao.remover}: ${a}`} className="hover:text-danger">
                  <Icon name="fechar" className="h-3.5 w-3.5" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {erro && (
        <p role="alert" className="text-danger text-sm">
          {erro}
        </p>
      )}

      <div className="flex gap-3">
        <Button type="submit" variante="primary" carregando={salvando}>
          {salvando ? textoSalvando : textoSalvar}
        </Button>
        <Button type="button" variante="ghost" onClick={onCancelar}>
          {t.novaQuestao.cancelar}
        </Button>
      </div>
    </form>
  );
}
