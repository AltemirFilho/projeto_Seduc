import { useEffect } from "react";

import { Button } from "./Button";

interface Props {
  aberto: boolean;
  titulo: string;
  mensagem: string;
  textoConfirmar: string;
  textoCancelar?: string;
  perigo?: boolean;
  carregando?: boolean;
  aoConfirmar: () => void;
  aoCancelar: () => void;
}

// Modal clay para ações irreversíveis (liberar/finalizar/excluir). Overlay deep-blue desfocado.
export function ConfirmDialog({
  aberto,
  titulo,
  mensagem,
  textoConfirmar,
  textoCancelar = "Cancelar",
  perigo,
  carregando,
  aoConfirmar,
  aoCancelar,
}: Props) {
  useEffect(() => {
    if (!aberto) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !carregando) aoCancelar();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [aberto, carregando, aoCancelar]);

  if (!aberto) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label={titulo}>
      <div
        className="absolute inset-0 bg-primary/40 backdrop-blur-sm"
        onClick={() => !carregando && aoCancelar()}
        aria-hidden="true"
      />
      <div className="relative bg-surface rounded-card shadow-clay p-6 sm:p-8 w-full max-w-md">
        <h2 className="text-xl font-bold text-text">{titulo}</h2>
        <p className="mt-2 text-text-muted">{mensagem}</p>
        <div className="mt-6 flex justify-end gap-3">
          <Button variante="ghost" onClick={aoCancelar} disabled={carregando}>
            {textoCancelar}
          </Button>
          <Button
            variante={perigo ? "danger" : "primary"}
            onClick={aoConfirmar}
            carregando={carregando}
            autoFocus
          >
            {textoConfirmar}
          </Button>
        </div>
      </div>
    </div>
  );
}
