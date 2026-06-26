import type { ReactNode } from "react";

// Ícones próprios (stroke, currentColor) — sem dependência de lib.
const formas: Record<string, ReactNode> = {
  dashboard: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="2" />
      <rect x="14" y="3" width="7" height="7" rx="2" />
      <rect x="14" y="14" width="7" height="7" rx="2" />
      <rect x="3" y="14" width="7" height="7" rx="2" />
    </>
  ),
  banco: (
    <>
      <path d="M4 7l8-4 8 4-8 4-8-4z" />
      <path d="M4 12l8 4 8-4" />
      <path d="M4 17l8 4 8-4" />
    </>
  ),
  importar: (
    <>
      <path d="M12 3v12" />
      <path d="M8 11l4 4 4-4" />
      <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
    </>
  ),
  simulados: (
    <>
      <rect x="5" y="3" width="14" height="18" rx="2" />
      <path d="M9 7h6" />
      <path d="M9 11h6" />
      <path d="M9 15h4" />
    </>
  ),
  prova: (
    <>
      <rect x="3" y="3" width="18" height="18" rx="3" />
      <circle cx="8" cy="8" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="16" cy="8" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="8" cy="16" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="16" cy="16" r="1.2" fill="currentColor" stroke="none" />
    </>
  ),
  turmas: (
    <>
      <circle cx="9" cy="8" r="3" />
      <path d="M3 20a6 6 0 0 1 12 0" />
      <path d="M16 6a3 3 0 0 1 0 6" />
      <path d="M18.5 20a6 6 0 0 0-3-5" />
    </>
  ),
  usuarios: (
    <>
      <circle cx="10" cy="8" r="3.2" />
      <path d="M4 20a6 6 0 0 1 12 0" />
      <path d="M19 8v6" />
      <path d="M16 11h6" />
    </>
  ),
  relatorios: (
    <>
      <path d="M5 21V11" />
      <path d="M12 21V4" />
      <path d="M19 21v-7" />
      <path d="M3 21h18" />
    </>
  ),
  diagnostico: (
    <>
      <path d="M11 3l1.7 4 4 1.7-4 1.7L11 14l-1.7-3.6L5.7 8.7l3.6-1.7z" />
      <circle cx="17.5" cy="17.5" r="2.5" />
    </>
  ),
  risco: (
    <>
      <path d="M12 3l9 16H3z" />
      <path d="M12 10v4" />
      <circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  perfil: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </>
  ),
  busca: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4-4" />
    </>
  ),
  sino: (
    <>
      <path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6z" />
      <path d="M10 20a2 2 0 0 0 4 0" />
    </>
  ),
  sair: (
    <>
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <path d="M16 17l5-5-5-5" />
      <path d="M21 12H9" />
    </>
  ),
  menu: (
    <>
      <path d="M3 6h18" />
      <path d="M3 12h18" />
      <path d="M3 18h18" />
    </>
  ),
  fechar: (
    <>
      <path d="M6 6l12 12" />
      <path d="M18 6L6 18" />
    </>
  ),
  check: <path d="M5 13l4 4L19 7" />,
  chevron: <path d="M6 9l6 6 6-6" />,
};

export function Icon({ name, className = "h-5 w-5" }: { name: string; className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {formas[name] ?? null}
    </svg>
  );
}
