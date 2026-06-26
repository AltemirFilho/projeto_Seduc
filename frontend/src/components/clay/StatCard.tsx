import type { ReactNode } from "react";

import { Skeleton } from "./Skeleton";

type Cor = "primary" | "accent" | "secondary" | "success";

// Pílula do ícone — todas com contraste AA (texto forte sobre pastel; branco só sobre cor saturada).
const pilula: Record<Cor, string> = {
  primary: "bg-primary text-on-primary",
  accent: "bg-accent text-white",
  secondary: "bg-secondary text-secondary-ink",
  success: "bg-success text-white",
};

interface Props {
  icone: ReactNode;
  rotulo: string;
  valor: ReactNode;
  cor?: Cor;
  carregando?: boolean;
  /** Marca dado mock (endpoint pendente) com a tag "exemplo". */
  exemplo?: boolean;
}

export function StatCard({ icone, rotulo, valor, cor = "primary", carregando, exemplo }: Props) {
  return (
    <div className="bg-surface rounded-card shadow-clay p-5 sm:p-6 flex items-center gap-4">
      <div className={`grid place-items-center h-12 w-12 rounded-2xl shadow-clay-sm shrink-0 ${pilula[cor]}`}>
        {icone}
      </div>
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm text-text-muted truncate">{rotulo}</p>
          {exemplo && (
            <span
              className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-chip bg-accent/15 text-accent-ink"
              title="Dado de exemplo — endpoint ainda não existe no backend"
            >
              exemplo
            </span>
          )}
        </div>
        {carregando ? (
          <Skeleton className="h-8 w-16 mt-1" />
        ) : (
          <p className="text-3xl font-display font-bold text-text leading-tight">{valor}</p>
        )}
      </div>
    </div>
  );
}
