import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { Button, Card, Field, Input, Select } from "../../components/clay";
import { ApiError } from "../../lib/api/client";
import { listarMaterias, listarSeries } from "../../lib/api/etiquetas";
import { criarSimulado, gerarSimulado } from "../../lib/api/simulados";
import { listarTurmas } from "../../lib/api/turmas";
import { t } from "../../i18n/pt-BR";

// C6 — Criar/montar simulado. POST /simulados + POST /{id}/gerar num passo, depois vai ao detalhe.
export function NovoSimuladoPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [titulo, setTitulo] = useState("");
  const [turmaId, setTurmaId] = useState("");
  const [serie, setSerie] = useState("");
  const [materia, setMateria] = useState("");
  const [quantidade, setQuantidade] = useState(10);
  const [seed, setSeed] = useState("");
  const [erroValidacao, setErroValidacao] = useState<string | null>(null);

  const turmas = useQuery({ queryKey: ["turmas"], queryFn: listarTurmas });
  const series = useQuery({ queryKey: ["etiquetas", "series"], queryFn: listarSeries });
  const materias = useQuery({ queryKey: ["etiquetas", "materias"], queryFn: listarMaterias });

  const mutation = useMutation({
    mutationFn: async () => {
      const seedNum = seed.trim() ? Number(seed) : undefined;
      const criado = await criarSimulado({
        turma_id: Number(turmaId),
        titulo: titulo.trim(),
        serie: serie.trim(),
        materia: materia.trim(),
        quantidade,
        seed: seedNum,
      });
      return gerarSimulado(criado.id, seedNum);
    },
    onSuccess: (resumo) => {
      queryClient.invalidateQueries({ queryKey: ["simulados"] });
      navigate(`/gestao/simulados/${resumo.id}`, { state: { resumo } });
    },
  });

  function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    if (!titulo.trim() || !turmaId || !serie.trim() || !materia.trim()) {
      setErroValidacao(t.novoSimulado.erroCampos);
      return;
    }
    setErroValidacao(null);
    mutation.mutate();
  }

  const erroServidor = mutation.error
    ? mutation.error instanceof ApiError
      ? mutation.error.message || t.novoSimulado.erro
      : t.novoSimulado.erro
    : null;
  const erro = erroValidacao ?? erroServidor;

  return (
    <form onSubmit={onSubmit} className="space-y-5 max-w-2xl" noValidate>
      <h1 className="text-2xl font-bold text-text">{t.novoSimulado.titulo}</h1>

      <Card className="space-y-4">
        <Field label={t.novoSimulado.campoTitulo} htmlFor="titulo">
          <Input
            id="titulo"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            placeholder={t.novoSimulado.tituloPlaceholder}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label={t.novoSimulado.turma} htmlFor="turma">
            <Select id="turma" value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
              <option value="">{t.novoSimulado.selecioneTurma}</option>
              {turmas.data?.map((tm) => (
                <option key={tm.id} value={tm.id}>
                  {tm.nome} — {tm.serie}
                </option>
              ))}
            </Select>
          </Field>

          <Field label={t.novoSimulado.serie} htmlFor="serie">
            <Input id="serie" list="lst-series" value={serie} onChange={(e) => setSerie(e.target.value)} />
            <datalist id="lst-series">
              {series.data?.map((s) => <option key={s.id} value={s.nome} />)}
            </datalist>
          </Field>

          <Field label={t.novoSimulado.materia} htmlFor="materia">
            <Input id="materia" list="lst-materias" value={materia} onChange={(e) => setMateria(e.target.value)} />
            <datalist id="lst-materias">
              {materias.data?.map((m) => <option key={m.id} value={m.nome} />)}
            </datalist>
          </Field>

          <Field label={t.novoSimulado.quantidade} htmlFor="quantidade">
            <Input
              id="quantidade"
              type="number"
              min={1}
              max={100}
              value={quantidade}
              onChange={(e) => setQuantidade(Math.max(1, Math.min(100, Number(e.target.value) || 1)))}
            />
          </Field>

          <Field label={t.novoSimulado.seed} htmlFor="seed">
            <Input id="seed" type="number" value={seed} onChange={(e) => setSeed(e.target.value)} placeholder="—" />
          </Field>
        </div>
        <p className="text-xs text-text-muted">{t.novoSimulado.seedDica}</p>
      </Card>

      {erro && (
        <p role="alert" className="text-danger text-sm">
          {erro}
        </p>
      )}

      <div className="flex gap-3">
        <Button type="submit" variante="primary" carregando={mutation.isPending}>
          {mutation.isPending ? t.novoSimulado.criando : t.novoSimulado.criar}
        </Button>
        <Button type="button" variante="ghost" onClick={() => navigate("/gestao/simulados")}>
          {t.novoSimulado.cancelar}
        </Button>
      </div>
    </form>
  );
}
