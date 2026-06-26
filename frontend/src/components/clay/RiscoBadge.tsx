import type { ClassificacaoRisco } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// Cores por classificação de risco (tokens --risco-*), texto escuro p/ AA (nunca branco sobre pastel).
// Fonte única — reusada na lista de alunos (C11) e no detalhe (C15).
export const CORES_RISCO: Record<ClassificacaoRisco, { bg: string; cor: string }> = {
  baixo: { bg: "rgba(79,157,107,0.15)", cor: "#2f6b47" },
  medio: { bg: "rgba(185,145,94,0.18)", cor: "#6e5226" },
  alto: { bg: "rgba(199,93,82,0.15)", cor: "#9e3f37" },
  indeterminado: { bg: "rgba(154,146,126,0.18)", cor: "#5c5341" },
};

// Chip compacto de risco de evasão (dot + label, opcional score %), no padrão do StatusBadge.
export function RiscoBadge({
  classificacao,
  score,
}: {
  classificacao: ClassificacaoRisco;
  score?: number;
}) {
  const c = CORES_RISCO[classificacao];
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-chip text-xs font-semibold"
      style={{ backgroundColor: c.bg, color: c.cor }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: c.cor }} aria-hidden="true" />
      {t.risco.classif[classificacao]}
      {score != null ? ` · ${Math.round(score * 100)}%` : ""}
    </span>
  );
}
