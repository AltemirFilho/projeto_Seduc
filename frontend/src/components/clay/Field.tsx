import type { ReactNode } from "react";

interface Props {
  label: string;
  htmlFor: string;
  erro?: string;
  children: ReactNode;
}

// Label acima, campo, e helper/erro abaixo (erro em --danger). Padrão dos forms (design_brief §3.4).
export function Field({ label, htmlFor, erro, children }: Props) {
  const erroId = `${htmlFor}-erro`;
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={htmlFor} className="text-sm font-semibold text-text">
        {label}
      </label>
      {children}
      {erro && (
        <p id={erroId} role="alert" className="text-sm text-danger">
          {erro}
        </p>
      )}
    </div>
  );
}
