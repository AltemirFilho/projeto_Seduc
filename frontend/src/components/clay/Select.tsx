import { forwardRef, type SelectHTMLAttributes } from "react";

// Chevron próprio (a aparência nativa é removida com appearance-none).
const CHEVRON =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none' stroke='%236F6A5C' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 6l4 4 4-4'/%3E%3C/svg%3E\")";

interface Props extends SelectHTMLAttributes<HTMLSelectElement> {
  invalido?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, Props>(function Select(
  { invalido = false, className, children, ...rest },
  ref,
) {
  return (
    <select
      ref={ref}
      aria-invalid={invalido || undefined}
      className={
        "w-full h-11 pl-3 pr-9 rounded-input bg-surface-sunken text-text shadow-clay-inset " +
        "appearance-none bg-no-repeat cursor-pointer " +
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary " +
        (invalido ? "ring-2 ring-danger " : "") +
        (className ?? "")
      }
      style={{ backgroundImage: CHEVRON, backgroundPosition: "right 0.75rem center", backgroundSize: "1rem" }}
      {...rest}
    >
      {children}
    </select>
  );
});
