// Placeholder de carregamento (pulsa) no tom creme afundado.
export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-surface-sunken ${className}`} aria-hidden="true" />;
}
