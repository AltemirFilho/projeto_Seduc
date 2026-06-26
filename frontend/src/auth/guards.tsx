import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "./AuthContext";
import { ehGestao } from "./perfil";

/** Exige sessão. Sem token → /login (guarda a rota de origem para voltar depois). */
export function RequireAuth() {
  const { autenticado } = useAuth();
  const loc = useLocation();
  if (!autenticado) {
    return <Navigate to="/login" replace state={{ de: loc.pathname }} />;
  }
  return <Outlet />;
}

/** Área da gestão (gestor/admin/suporte). Logado sem perfil → /sem-acesso. */
export function RequireGestao() {
  const { usuario } = useAuth();
  if (!usuario) return <Navigate to="/login" replace />;
  if (!ehGestao(usuario.perfil)) return <Navigate to="/sem-acesso" replace />;
  return <Outlet />;
}

/** Área do aluno. Logado com outro perfil → /sem-acesso. */
export function RequireAluno() {
  const { usuario } = useAuth();
  if (!usuario) return <Navigate to="/login" replace />;
  if (usuario.perfil !== "aluno") return <Navigate to="/sem-acesso" replace />;
  return <Outlet />;
}
