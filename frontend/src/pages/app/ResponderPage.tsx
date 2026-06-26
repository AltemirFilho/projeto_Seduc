import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { Button, Card, ConfirmDialog, Skeleton, Spinner } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { questoesDoAluno, salvarResposta } from "../../lib/api/simulados";
import { t } from "../../i18n/pt-BR";

// B3 — Realizar simulado. Uma questão por vez, autosave via POST /respostas (sem gabarito).
export function ResponderPage() {
  const { id } = useParams();
  const idNum = Number(id);
  const location = useLocation();
  const titulo = (location.state as { titulo?: string } | null)?.titulo;

  const [indice, setIndice] = useState(0);
  const [respostas, setRespostas] = useState<Record<number, number>>({});
  const [confirmar, setConfirmar] = useState(false);
  const [entregue, setEntregue] = useState(false);

  const query = useQuery({
    queryKey: ["aluno", "questoes", idNum],
    queryFn: () => questoesDoAluno(idNum),
  });

  const salvar = useMutation({
    mutationFn: (v: { questao_id: number; alternativa_id: number }) =>
      salvarResposta({ simulado_id: idNum, ...v }),
  });

  function escolher(questaoId: number, altId: number) {
    setRespostas((r) => ({ ...r, [questaoId]: altId }));
    salvar.mutate({ questao_id: questaoId, alternativa_id: altId });
  }

  const questoes = query.data?.questoes ?? [];
  const atual = questoes[indice];
  const respondidas = Object.keys(respostas).length;

  if (query.isLoading) {
    return (
      <Card className="max-w-2xl space-y-3">
        <Skeleton className="h-6 w-1/3" />
        <Skeleton className="h-32 w-full" />
      </Card>
    );
  }
  if (query.isError) {
    return (
      <Card className="max-w-2xl">
        <p className="text-danger">{t.responder.erro}</p>
      </Card>
    );
  }
  if (questoes.length === 0) {
    return (
      <Card className="max-w-2xl">
        <p className="text-text-muted">{t.responder.semQuestoes}</p>
      </Card>
    );
  }

  if (entregue) {
    return (
      <Card className="max-w-2xl text-center py-10">
        <div className="mx-auto grid place-items-center h-14 w-14 rounded-full bg-success text-white mb-4">
          <Icon name="check" className="h-7 w-7" />
        </div>
        <h1 className="text-2xl font-bold text-text">{t.responder.entregue}</h1>
        <p className="text-text-muted mt-2">{t.responder.entregueMsg}</p>
        <div className="mt-6">
          <Link to="/app/simulados">
            <Button variante="secondary">{t.responder.voltar}</Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl space-y-5">
      <div>
        <Link to="/app/simulados" className="text-sm text-primary hover:underline">
          {t.responder.voltar}
        </Link>
        <h1 className="text-xl font-bold text-text mt-1">{titulo ?? `Simulado #${idNum}`}</h1>
        <div className="flex items-center gap-3 mt-1 text-sm text-text-muted">
          <span>{t.responder.questaoDe(indice + 1, questoes.length)}</span>
          <span aria-hidden="true">·</span>
          <span>{t.responder.progresso(respondidas, questoes.length)}</span>
          <SaveStatus pendente={salvar.isPending} sucesso={salvar.isSuccess} erro={salvar.isError} />
        </div>
      </div>

      {/* Navegador de questões */}
      <div className="flex flex-wrap gap-2">
        {questoes.map((q, i) => {
          const respondida = respostas[q.questao_id] !== undefined;
          const ativa = i === indice;
          return (
            <button
              key={q.questao_id}
              onClick={() => setIndice(i)}
              aria-label={`Questão ${i + 1}`}
              aria-current={ativa || undefined}
              className={
                "h-8 w-8 rounded-full text-xs font-semibold transition-colors " +
                (ativa ? "ring-2 ring-primary " : "") +
                (respondida ? "bg-success text-white" : "bg-surface-sunken text-text-muted")
              }
            >
              {i + 1}
            </button>
          );
        })}
      </div>

      {/* Questão atual */}
      <Card className="space-y-4">
        <div>
          <p className="text-xs text-text-muted">
            {atual.conteudo} · {atual.nivel}
          </p>
          <p className="text-text font-medium text-lg mt-1">{atual.enunciado}</p>
        </div>
        <div className="space-y-2">
          {atual.alternativas.map((alt) => {
            const selecionada = respostas[atual.questao_id] === alt.alternativa_id;
            return (
              <button
                key={alt.alternativa_id}
                type="button"
                onClick={() => escolher(atual.questao_id, alt.alternativa_id)}
                className={
                  "w-full text-left flex items-start gap-3 p-4 rounded-2xl transition-all " +
                  (selecionada
                    ? "bg-secondary/40 shadow-clay-inset"
                    : "bg-surface shadow-clay-sm hover:-translate-y-0.5")
                }
              >
                <span
                  className={
                    "grid place-items-center h-7 w-7 rounded-full shrink-0 text-sm font-semibold " +
                    (selecionada ? "bg-primary text-on-primary" : "bg-surface-sunken text-text-muted")
                  }
                >
                  {alt.letra}
                </span>
                <span className="text-text pt-0.5">{alt.texto}</span>
              </button>
            );
          })}
        </div>
        {salvar.isError && <p className="text-danger text-sm">{t.responder.erroSalvar}</p>}
      </Card>

      {/* Rodapé de navegação */}
      <div className="flex items-center justify-between gap-3">
        <Button variante="secondary" tamanho="sm" disabled={indice <= 0} onClick={() => setIndice((i) => i - 1)}>
          {t.responder.anterior}
        </Button>
        {indice < questoes.length - 1 ? (
          <Button variante="secondary" tamanho="sm" onClick={() => setIndice((i) => i + 1)}>
            {t.responder.proxima}
          </Button>
        ) : (
          <Button variante="primary" tamanho="sm" onClick={() => setConfirmar(true)}>
            {t.responder.entregar}
          </Button>
        )}
      </div>

      <ConfirmDialog
        aberto={confirmar}
        titulo={t.responder.entregarTitulo}
        mensagem={t.responder.entregarMsg}
        textoConfirmar={t.responder.entregar}
        aoConfirmar={() => {
          setConfirmar(false);
          setEntregue(true);
        }}
        aoCancelar={() => setConfirmar(false)}
      />
    </div>
  );
}

function SaveStatus({ pendente, sucesso, erro }: { pendente: boolean; sucesso: boolean; erro: boolean }) {
  if (pendente)
    return (
      <span className="inline-flex items-center gap-1 text-text-muted">
        <Spinner className="h-3.5 w-3.5" /> {t.responder.salvando}
      </span>
    );
  if (erro) return <span className="text-danger">{t.responder.erroSalvar}</span>;
  if (sucesso)
    return (
      <span className="inline-flex items-center gap-1 text-success">
        <Icon name="check" className="h-3.5 w-3.5" /> {t.responder.salvo}
      </span>
    );
  return null;
}
