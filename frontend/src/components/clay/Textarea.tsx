import { forwardRef, type TextareaHTMLAttributes } from "react";

interface Props extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalido?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, Props>(function Textarea(
  { invalido = false, className, ...rest },
  ref,
) {
  return (
    <textarea
      ref={ref}
      aria-invalid={invalido || undefined}
      className={
        "w-full min-h-[96px] px-4 py-3 rounded-input bg-surface-sunken text-text " +
        "placeholder:text-text-muted/70 shadow-clay-inset transition-shadow resize-y " +
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary " +
        (invalido ? "ring-2 ring-danger " : "") +
        (className ?? "")
      }
      {...rest}
    />
  );
});
