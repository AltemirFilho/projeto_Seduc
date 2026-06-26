import type { StatusSimulado } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// Chip de status do simulado: fundo com tint da cor + texto/forte em variante escura (AA).
const MAPA: Record<StatusSimulado, { bg: string; cor: string }> = {
  rascunho: { bg: "rgba(154,146,126,0.18)", cor: "#5c5341" },
  gerado: { bg: "rgba(94,134,194,0.18)", cor: "#274c84" },
  liberado: { bg: "rgba(79,157,107,0.18)", cor: "#2c6243" },
  finalizado: { bg: "rgba(24,35,80,0.12)", cor: "#182350" },
};

export function StatusBadge({ status }: { status: StatusSimulado }) {
  const m = MAPA[status];
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-chip text-xs font-semibold"
      style={{ backgroundColor: m.bg, color: m.cor }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: m.cor }} aria-hidden="true" />
      {t.statusSimulado[status]}
    </span>
  );
}
