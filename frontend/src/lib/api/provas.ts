import type { GerarProvaParams, ProvaGerada } from "../../types/api";
import { apiFetch } from "./client";

/** POST /provas/gerar → prova avulsa (sorteio balanceado + embaralhamento). Requer gestor. */
export function gerarProva(params: GerarProvaParams): Promise<ProvaGerada> {
  return apiFetch<ProvaGerada>("/provas/gerar", { method: "POST", body: params });
}
