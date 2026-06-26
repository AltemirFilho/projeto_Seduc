import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useNavigate } from "react-router-dom";

import { registrarHandlerSessao } from "../lib/api/client";
import type { UsuarioOut } from "../types/api";
import { clearSession, getUsuario, saveSession } from "./storage";

interface AuthCtx {
  usuario: UsuarioOut | null;
  autenticado: boolean;
  entrar: (token: string, usuario: UsuarioOut) => void;
  sair: () => void;
}

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  // Hidrata da sessão salva (sobrevive a refresh).
  const [usuario, setUsuario] = useState<UsuarioOut | null>(() => getUsuario());

  const entrar = useCallback((token: string, u: UsuarioOut) => {
    saveSession(token, u);
    setUsuario(u);
  }, []);

  const sair = useCallback(() => {
    clearSession();
    setUsuario(null);
    navigate("/login", { replace: true });
  }, [navigate]);

  // Quando o client detecta sessão inválida (403 token), ele já limpou o storage;
  // aqui só refletimos no estado e mandamos pro login.
  useEffect(() => {
    registrarHandlerSessao(() => {
      setUsuario(null);
      navigate("/login", { replace: true });
    });
  }, [navigate]);

  const valor = useMemo<AuthCtx>(
    () => ({ usuario, autenticado: usuario !== null, entrar, sair }),
    [usuario, entrar, sair],
  );

  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthCtx {
  const ctx = useContext(Ctx);
  if (ctx === null) throw new Error("useAuth deve ser usado dentro de <AuthProvider>");
  return ctx;
}
