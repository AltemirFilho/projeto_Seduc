import type { Diagnostico, Risco } from "../../types/api";
import { apiFetch } from "./client";

/** GET /ia/risco/{aluno_id} → calcula (sklearn), salva e devolve. Requer gestor. */
export function riscoDoAluno(alunoId: number): Promise<Risco> {
  return apiFetch<Risco>(`/ia/risco/${alunoId}`);
}

/** GET /ia/diagnostico/{simulado_id} → diagnóstico da turma (exige FINALIZADO, senão 409). */
export function diagnosticoDoSimulado(simuladoId: number): Promise<Diagnostico> {
  return apiFetch<Diagnostico>(`/ia/diagnostico/${simuladoId}`);
}
