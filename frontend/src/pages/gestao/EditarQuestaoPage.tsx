import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";

import { Card, Skeleton } from "../../components/clay";
import { ApiError } from "../../lib/api/client";
import { atualizarQuestao, obterQuestao } from "../../lib/api/questoes";
import type { NovaQuestao } from "../../types/api";
import { QuestaoForm } from "./QuestaoForm";
import { t } from "../../i18n/pt-BR";

// C4 — Editar questão. GET /questoes/{id} para preencher, PATCH para salvar.
// Questão já usada em simulado é congelada → 409 `questao_em_uso`.
export function EditarQuestaoPage() {
  const { id } = useParams();
  const idNum = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const query = useQuery({ queryKey: ["questao", idNum], queryFn: () => obterQuestao(idNum) });

  const mutation = useMutation({
    mutationFn: (p: NovaQuestao) => atualizarQuestao(idNum, p),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questoes"] });
      queryClient.invalidateQueries({ queryKey: ["questao", idNum] });
      navigate(`/gestao/questoes/${idNum}`);
    },
  });

  const erroServidor =
    mutation.error instanceof ApiError
      ? mutation.error.codigo === "questao_em_uso"
        ? t.editarQuestao.emUso
        : mutation.error.message || t.editarQuestao.erroSalvar
      : mutation.error
        ? t.editarQuestao.erroSalvar
        : null;

  return (
    <div className="space-y-5 max-w-3xl">
      <h1 className="text-2xl font-bold text-text">{t.editarQuestao.titulo}</h1>

      {query.isLoading ? (
        <Card className="space-y-3">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-32 w-full" />
        </Card>
      ) : query.isError ? (
        <Card>
          <p className="text-danger">
            {query.error instanceof ApiError && query.error.status === 404
              ? t.questaoDetalhe.naoEncontrada
              : t.editarQuestao.erroCarregar}
          </p>
        </Card>
      ) : query.data ? (
        <QuestaoForm
          inicial={query.data}
          salvando={mutation.isPending}
          erroServidor={erroServidor}
          textoSalvar={t.editarQuestao.salvar}
          textoSalvando={t.novaQuestao.salvando}
          onSubmit={(p) => mutation.mutate(p)}
          onCancelar={() => navigate(`/gestao/questoes/${idNum}`)}
        />
      ) : null}
    </div>
  );
}
