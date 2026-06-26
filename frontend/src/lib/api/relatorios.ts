import type { RelatorioTurma } from "../../types/api";
import { getToken } from "../../auth/storage";
import { apiFetch } from "./client";

const BASE_URL =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://127.0.0.1:8000";

/** GET /relatorios/turma/{id} → desempenho da turma. Requer gestor. */
export function relatorioTurma(turmaId: number): Promise<RelatorioTurma> {
  return apiFetch<RelatorioTurma>(`/relatorios/turma/${turmaId}`);
}

/** Baixa o export (CSV/PDF) com o Bearer e dispara o download no browser. */
export async function baixarRelatorioTurma(
  turmaId: number,
  formato: "csv" | "pdf",
): Promise<void> {
  const resp = await fetch(
    `${BASE_URL}/relatorios/turma/${turmaId}/export?formato=${formato}`,
    { headers: { Authorization: `Bearer ${getToken() ?? ""}` } },
  );
  if (!resp.ok) throw new Error("falha ao exportar relatório");
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `relatorio_turma_${turmaId}.${formato}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
