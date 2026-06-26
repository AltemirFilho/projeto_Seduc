import type { UsuarioOut } from "../types/api";

// O backend usa JWT em header Authorization (não cookie) → localStorage é o ajuste natural.
const TOKEN_KEY = "seduc.token";
const USUARIO_KEY = "seduc.usuario";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getUsuario(): UsuarioOut | null {
  try {
    const raw = localStorage.getItem(USUARIO_KEY);
    return raw ? (JSON.parse(raw) as UsuarioOut) : null;
  } catch {
    return null;
  }
}

export function saveSession(token: string, usuario: UsuarioOut): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USUARIO_KEY, JSON.stringify(usuario));
  } catch {
    /* storage indisponível (modo privado): segue só em memória via estado do React */
  }
}

export function clearSession(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USUARIO_KEY);
  } catch {
    /* noop */
  }
}
