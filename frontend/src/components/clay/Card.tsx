import type { HTMLAttributes } from "react";

// Superfície elevada "puffy" — sombra dupla clay, raio grande, sem borda.
export function Card({ className, children, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`bg-surface rounded-card shadow-clay p-6 sm:p-8 ${className ?? ""}`} {...rest}>
      {children}
    </div>
  );
}
