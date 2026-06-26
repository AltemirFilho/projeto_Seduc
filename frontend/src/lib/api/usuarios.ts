import type { NovoUsuario, Usuario } from "../../types/api";
import { apiFetch } from "./client";

export interface ListaUsuarios {
  dados: Usuario[];
  meta: { total: number };
}

/** GET /usuarios?perfil&turma_id → lista (envelope com meta.total). Requer gestor. */
export function listarUsuarios(
  filtro: { perfil?: string; turma_id?: number } = {},
): Promise<ListaUsuarios> {
  const p = new URLSearchParams();
  if (filtro.perfil) p.set("perfil", filtro.perfil);
  if (filtro.turma_id != null) p.set("turma_id", String(filtro.turma_id));
  const q = p.toString();
  return apiFetch<ListaUsuarios>(`/usuarios${q ? `?${q}` : ""}`);
}

/** POST /usuarios → cadastra usuário (aluno precisa de turma_id). Requer gestor. */
export function criarUsuario(payload: NovoUsuario): Promise<Usuario> {
  return apiFetch<Usuario>("/usuarios", { method: "POST", body: payload });
}
