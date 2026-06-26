import type { TokenOut, UsuarioOut } from "../../types/api";
import { apiFetch } from "./client";

/** POST /auth/login → token + usuário. `auth:false`: a chamada de login não leva Bearer. */
export function login(email: string, senha: string): Promise<TokenOut> {
  return apiFetch<TokenOut>("/auth/login", {
    method: "POST",
    body: { email, senha },
    auth: false,
  });
}

/** GET /auth/me → dados do usuário do token (usado para validar a sessão hidratada). */
export function me(): Promise<UsuarioOut> {
  return apiFetch<UsuarioOut>("/auth/me");
}
