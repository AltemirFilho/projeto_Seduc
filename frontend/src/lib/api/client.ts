// Cliente HTTP tipado. Injeta o JWT (Bearer), normaliza os DOIS formatos de erro
// do backend e centraliza o tratamento de sessão inválida.
//
// Contrato de auth confirmado no backend (app/api/deps.py, auth.py, exceptions.py):
//   - NÃO existe 401 em lugar nenhum — toda falha de auth volta como 403.
//   - 403 "credenciais_invalidas" .... login errado  (tratado localmente na tela de login)
//   - 403 "token_invalido" ............ token expirado/inválido → relogar
//   - 403 {detail:"Not authenticated"} token ausente (HTTPBearer cru) → relogar
//   - 403 "perfil_insuficiente"/"sem_permissao" .. logado, mas sem o perfil → /sem-acesso
// Por isso a decisão é pelo `codigo`, não pelo status.

import { clearSession, getToken } from "../../auth/storage";

const BASE_URL =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  readonly status: number;
  readonly codigo: string;
  readonly detalhes?: unknown;

  constructor(status: number, codigo: string, mensagem: string, detalhes?: unknown) {
    super(mensagem);
    this.name = "ApiError";
    this.status = status;
    this.codigo = codigo;
    this.detalhes = detalhes;
  }

  /** Sessão expirou / token ausente → precisa relogar. */
  get sessaoInvalida(): boolean {
    return (
      this.status === 403 &&
      (this.codigo === "token_invalido" || this.codigo === "nao_autenticado")
    );
  }

  /** Logado, mas sem permissão de perfil → tela "sem acesso". */
  get semPermissao(): boolean {
    return (
      this.status === 403 &&
      (this.codigo === "sem_permissao" || this.codigo === "perfil_insuficiente")
    );
  }
}

// O client não conhece o router. O AuthContext registra aqui o que fazer quando
// a sessão cai (atualizar estado + mandar pro /login).
let aoInvalidarSessao: (() => void) | null = null;
export function registrarHandlerSessao(fn: () => void): void {
  aoInvalidarSessao = fn;
}

interface Opcoes {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  /** Injeta Authorization: Bearer <token>. Default true (login usa false). */
  auth?: boolean;
  signal?: AbortSignal;
}

export async function apiFetch<T>(caminho: string, opcoes: Opcoes = {}): Promise<T> {
  const { method = "GET", body, auth = true, signal } = opcoes;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let resp: Response;
  try {
    resp = await fetch(`${BASE_URL}${caminho}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (e) {
    if ((e as Error).name === "AbortError") throw e;
    throw new ApiError(0, "rede", "Não foi possível conectar ao servidor. Verifique sua conexão.");
  }

  if (resp.status === 204) return undefined as T;

  // O corpo pode vir vazio; tentar JSON com cuidado.
  let dados: unknown = null;
  const texto = await resp.text();
  if (texto) {
    try {
      dados = JSON.parse(texto);
    } catch {
      dados = null;
    }
  }

  if (!resp.ok) {
    const erro = normalizarErro(resp.status, dados);
    if (erro.sessaoInvalida) {
      clearSession();
      aoInvalidarSessao?.();
    }
    throw erro;
  }

  return dados as T;
}

function normalizarErro(status: number, dados: unknown): ApiError {
  const obj = (dados ?? {}) as Record<string, unknown>;

  // Formato de domínio do backend: { codigo, mensagem }
  if (typeof obj.codigo === "string") {
    const mensagem = typeof obj.mensagem === "string" ? obj.mensagem : "Erro inesperado.";
    return new ApiError(status, obj.codigo, mensagem, obj.detalhes);
  }

  // Formato cru do FastAPI: { detail } (ex.: token ausente no HTTPBearer → 403 "Not authenticated")
  if (obj.detail !== undefined) {
    const detail = typeof obj.detail === "string" ? obj.detail : "Requisição inválida.";
    const naoAutenticado = status === 403 && /not authenticated/i.test(detail);
    const codigo = naoAutenticado ? "nao_autenticado" : `http_${status}`;
    const mensagem = naoAutenticado ? "Sua sessão expirou. Entre novamente." : detail;
    return new ApiError(status, codigo, mensagem, obj.detail);
  }

  // Corpo vazio → mensagem padrão por status.
  const padrao: Record<number, [string, string]> = {
    403: ["sem_permissao", "Você não tem acesso a este recurso."],
    404: ["nao_encontrado", "Recurso não encontrado."],
    409: ["regra_negocio", "Operação não permitida pelas regras do sistema."],
    422: ["dados_invalidos", "Dados inválidos."],
    500: ["erro_servidor", "Erro no servidor. Tente novamente."],
  };
  const [codigo, mensagem] = padrao[status] ?? [`http_${status}`, "Ocorreu um erro inesperado."];
  return new ApiError(status, codigo, mensagem);
}
