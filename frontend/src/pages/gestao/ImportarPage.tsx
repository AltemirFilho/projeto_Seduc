import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { Button, Card, Textarea } from "../../components/clay";
import { ApiError } from "../../lib/api/client";
import { importarQuestoes } from "../../lib/api/questoes";
import type { ResultadoImportacao } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// Importar questões em lote (POST /questoes/import) a partir de um JSON colado.
export function ImportarPage() {
  const [json, setJson] = useState("");
  const [erroLocal, setErroLocal] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoImportacao | null>(null);

  const mutation = useMutation({
    mutationFn: (questoes: unknown[]) => importarQuestoes(questoes),
    onSuccess: (r) => {
      setResultado(r);
      setErroLocal(null);
    },
  });

  function importar() {
    let parsed: unknown;
    try {
      parsed = JSON.parse(json);
    } catch {
      setErroLocal(t.importar.jsonInvalido);
      return;
    }
    if (!Array.isArray(parsed)) {
      setErroLocal(t.importar.jsonInvalido);
      return;
    }
    setErroLocal(null);
    setResultado(null);
    mutation.mutate(parsed);
  }

  const erro =
    erroLocal ??
    (mutation.error
      ? mutation.error instanceof ApiError
        ? mutation.error.message || t.importar.erro
        : t.importar.erro
      : null);

  return (
    <div className="space-y-5 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-text">{t.importar.titulo}</h1>
        <p className="text-text-muted mt-0.5">{t.importar.sub}</p>
      </div>

      <Card className="space-y-3">
        <label htmlFor="json" className="text-sm font-semibold text-text">
          {t.importar.label}
        </label>
        <Textarea
          id="json"
          value={json}
          onChange={(e) => setJson(e.target.value)}
          placeholder={t.importar.placeholder}
          className="min-h-[220px] font-mono text-xs"
        />
        <div className="flex gap-3">
          <Button variante="primary" carregando={mutation.isPending} disabled={!json.trim()} onClick={importar}>
            {mutation.isPending ? t.importar.importando : t.importar.importar}
          </Button>
          <Button
            variante="ghost"
            onClick={() => {
              setJson("");
              setResultado(null);
              setErroLocal(null);
            }}
          >
            {t.importar.limpar}
          </Button>
        </div>
        {erro && (
          <p role="alert" className="text-danger text-sm">
            {erro}
          </p>
        )}
      </Card>

      {resultado && (
        <Card className={resultado.rejeitadas === 0 ? "bg-success/10" : ""}>
          <p className="font-semibold text-text">
            {t.importar.resultado(resultado.importadas, resultado.rejeitadas)}
          </p>
          {resultado.erros.length > 0 && (
            <div className="mt-3">
              <p className="text-sm font-semibold text-text mb-1">{t.importar.errosTitulo}</p>
              <ul className="space-y-1 text-sm text-danger">
                {resultado.erros.map((e, i) => (
                  <li key={i}>
                    {t.importar.linha} {e.linha}: {e.motivo}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
