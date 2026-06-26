import type { Perfil } from "../types/api";

/** Gestão = gestor / admin / suporte (suporte é leitura). Aluno tem painel próprio. */
export function ehGestao(perfil: Perfil): boolean {
  return perfil === "admin" || perfil === "gestor" || perfil === "suporte";
}

/** Para onde redirecionar após o login, conforme o perfil. */
export function rotaInicialPorPerfil(perfil: Perfil): string {
  return perfil === "aluno" ? "/app" : "/gestao";
}
