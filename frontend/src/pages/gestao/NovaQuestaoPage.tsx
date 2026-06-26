import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { ApiError } from "../../lib/api/client";
import { criarQuestao } from "../../lib/api/questoes";
import { QuestaoForm } from "./QuestaoForm";
import { t } from "../../i18n/pt-BR";

// C3 — Criar questão objetiva. POST /questoes (form compartilhado com a edição).
export function NovaQuestaoPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: criarQuestao,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questoes"] });
      navigate("/gestao/questoes");
    },
  });

  const erroServidor = mutation.error
    ? mutation.error instanceof ApiError
      ? mutation.error.message || t.novaQuestao.erroSalvar
      : t.novaQuestao.erroSalvar
    : null;

  return (
    <div className="space-y-5 max-w-3xl">
      <h1 className="text-2xl font-bold text-text">{t.novaQuestao.titulo}</h1>
      <QuestaoForm
        salvando={mutation.isPending}
        erroServidor={erroServidor}
        textoSalvar={t.novaQuestao.salvar}
        textoSalvando={t.novaQuestao.salvando}
        onSubmit={(p) => mutation.mutate(p)}
        onCancelar={() => navigate("/gestao/questoes")}
      />
    </div>
  );
}
