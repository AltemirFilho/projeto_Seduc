import type { Turma } from "../../types/api";
import { apiFetch } from "./client";

/** GET /turmas → lista flat (não envelopada). Requer perfil de gestão. */
export function listarTurmas(): Promise<Turma[]> {
  return apiFetch<Turma[]>("/turmas");
}
