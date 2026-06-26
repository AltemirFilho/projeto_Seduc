import { forwardRef, type InputHTMLAttributes } from "react";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  invalido?: boolean;
}

// Campo "afundado" (clay-inset) sobre o creme; anel de foco para acessibilidade.
export const Input = forwardRef<HTMLInputElement, Props>(function Input(
  { invalido = false, className, ...rest },
  ref,
) {
  return (
    <input
      ref={ref}
      aria-invalid={invalido || undefined}
      className={
        "w-full h-11 px-4 rounded-input bg-surface-sunken text-text " +
        "placeholder:text-text-muted/70 shadow-clay-inset transition-shadow " +
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary " +
        (invalido ? "ring-2 ring-danger " : "") +
        (className ?? "")
      }
      {...rest}
    />
  );
});
