import { forwardRef, type ButtonHTMLAttributes } from "react";

import { Spinner } from "./Spinner";

type Variante = "primary" | "secondary" | "ghost" | "danger";
type Tamanho = "sm" | "md" | "lg";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante;
  tamanho?: Tamanho;
  carregando?: boolean;
  blocoCompleto?: boolean;
}

const base =
  "inline-flex items-center justify-center gap-2 font-display font-semibold rounded-btn " +
  "transition-[transform,box-shadow,background-color] duration-150 select-none " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary " +
  "focus-visible:ring-offset-2 focus-visible:ring-offset-bg " +
  "disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98]";

// Contraste AA: primary/danger usam preenchimento forte com texto creme/branco;
// secondary/ghost usam texto na cor forte sobre superfície clara.
const variantes: Record<Variante, string> = {
  primary: "bg-primary text-on-primary shadow-clay-sm hover:bg-primary-hover active:shadow-clay-inset",
  secondary: "bg-surface text-primary shadow-clay-sm hover:-translate-y-px active:shadow-clay-inset",
  ghost: "bg-transparent text-primary hover:bg-surface-sunken",
  danger: "bg-danger text-white shadow-clay-sm hover:brightness-105 active:shadow-clay-inset",
};

// Alvo de toque ≥ 44px (md e lg cumprem; sm para ações densas).
const tamanhos: Record<Tamanho, string> = {
  sm: "h-9 px-4 text-sm",
  md: "h-11 px-5 text-[15px]",
  lg: "h-12 px-7 text-base",
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variante = "primary", tamanho = "md", carregando = false, blocoCompleto = false, className, children, disabled, ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      disabled={disabled || carregando}
      aria-busy={carregando || undefined}
      className={`${base} ${variantes[variante]} ${tamanhos[tamanho]} ${blocoCompleto ? "w-full" : ""} ${className ?? ""}`}
      {...rest}
    >
      {carregando && <Spinner className="h-4 w-4" />}
      {children}
    </button>
  );
});
