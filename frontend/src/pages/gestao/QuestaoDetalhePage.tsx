import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { Button, Card, Skeleton } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { ApiError } from "../../lib/api/client";
import { obterQuestao } from "../../lib/api/questoes";
import type { Questao } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// C4 — Ver questão (read-only, com gabarito). A edição (PATCH /questoes/:id) não existe
// no backend ainda — botão Editar fica desabilitado com aviso (combinar com o Altemir).
export function QuestaoDetalhePage() {
  const { id } = useParams();
  const location = useLocation();
  const idNum = Number(id);
  // Ao vir da lista, a questão chega via state (evita refetch); fallback busca pela lista.
  const questaoInicial = (location.state as { questao?: Questao } | null)?.questao;

  const query = useQuery({
    queryKey: ["questao", idNum],
    queryFn: () => obterQuestao(idNum),
    initialData: questaoInicial && questaoInicial.id === idNum ? questaoInicial : undefined,
  });

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-text">{t.questaoDetalhe.titulo}</h1>
        <div className="flex gap-2">
          <Link to="/gestao/questoes">
            <Button variante="ghost" tamanho="sm">
              {t.questaoDetalhe.voltar}
            </Button>
          </Link>
          <Link to={`/gestao/questoes/${idNum}/editar`}>
            <Button variante="primary" tamanho="sm">
              {t.questaoDetalhe.editar}
            </Button>
          </Link>
        </div>
      </div>

      {query.isLoading ? (
        <Card className="space-y-3">
          <Skeleton className="h-6 w-2/3" />
          <Skeleton className="h-24 w-full" />
        </Card>
      ) : query.isError ? (
        <Card>
          <p className={query.error instanceof ApiError && query.error.status === 404 ? "text-text-muted" : "text-danger"}>
            {query.error instanceof ApiError && query.error.status === 404
              ? t.questaoDetalhe.naoEncontrada
              : t.questaoDetalhe.erro}
          </p>
        </Card>
      ) : !query.data ? (
        <Card>
          <Skeleton className="h-24 w-full" />
        </Card>
      ) : (
        <Detalhe q={query.data} />
      )}
    </div>
  );
}

function Detalhe({ q }: { q: Questao }) {
  return (
    <>
      <Card className="space-y-3">
        <h2 className="font-display font-bold text-text">{t.questaoDetalhe.classificacao}</h2>
        <div className="flex flex-wrap gap-2">
          <Chip>{q.serie}</Chip>
          <Chip>{q.materia}</Chip>
          <Chip>{q.conteudo}</Chip>
          <span className="px-2.5 py-1 rounded-chip bg-secondary/40 text-secondary-ink text-sm font-medium">
            {q.nivel}
          </span>
        </div>
        {q.adaptacoes.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-1">
            {q.adaptacoes.map((a) => (
              <span key={a} className="px-2.5 py-1 rounded-chip bg-accent/15 text-accent-ink text-sm">
                {a}
              </span>
            ))}
          </div>
        )}
      </Card>

      <Card className="space-y-2">
        <h2 className="font-display font-bold text-text">{t.questaoDetalhe.enunciado}</h2>
        <p className="text-text whitespace-pre-wrap">{q.enunciado}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="font-display font-bold text-text">{t.questaoDetalhe.alternativas}</h2>
        <ul className="space-y-2">
          {q.alternativas.map((alt, i) => (
            <li
              key={alt.id}
              className={
                "flex items-start gap-3 p-3 rounded-2xl " +
                (alt.correta ? "bg-success/10" : "bg-surface-sunken/60")
              }
            >
              <span
                className={
                  "grid place-items-center h-7 w-7 rounded-full shrink-0 text-sm font-semibold " +
                  (alt.correta ? "bg-success text-white" : "bg-surface text-text-muted shadow-clay-sm")
                }
              >
                {String.fromCharCode(65 + i)}
              </span>
              <span className="text-text pt-0.5">{alt.texto}</span>
              {alt.correta && (
                <span className="ml-auto shrink-0 inline-flex items-center gap-1 text-success text-sm font-semibold">
                  <Icon name="check" className="h-4 w-4" />
                  {t.questaoDetalhe.correta}
                </span>
              )}
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}

function Chip({ children }: { children: ReactNode }) {
  return <span className="px-2.5 py-1 rounded-chip bg-surface-sunken text-text-muted text-sm">{children}</span>;
}
