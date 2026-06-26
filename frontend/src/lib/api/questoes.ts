import type { Envelope, NovaQuestao, Questao, ResultadoImportacao } from "../../types/api";
import { apiFetch } from "./client";

export interface FiltroQuestoes {
  serie?: string;
  materia?: string;
  conteudo?: string;
  nivel?: string;
  pagina?: number;
  por_pagina?: number;
}

function querystring(filtro: FiltroQuestoes): string {
  const p = new URLSearchParams();
  for (const [chave, valor] of Object.entries(filtro)) {
    if (valor !== undefined && valor !== null && valor !== "") p.set(chave, String(valor));
  }
  const s = p.toString();
  return s ? `?${s}` : "";
}

/** GET /questoes (paginado, envelope {dados,meta}). Requer perfil de gestão. */
export function listarQuestoes(filtro: FiltroQuestoes = {}): Promise<Envelope<Questao>> {
  return apiFetch<Envelope<Questao>>(`/questoes${querystring(filtro)}`);
}

/** Só o total (meta.total) para um filtro — usa página mínima. */
export function contarQuestoes(
  filtro: Omit<FiltroQuestoes, "pagina" | "por_pagina"> = {},
): Promise<number> {
  return listarQuestoes({ ...filtro, pagina: 1, por_pagina: 1 }).then((r) => r.meta.total);
}

/** POST /questoes → questão criada. Requer perfil de gestão. */
export function criarQuestao(payload: NovaQuestao): Promise<Questao> {
  return apiFetch<Questao>("/questoes", { method: "POST", body: payload });
}

/** GET /questoes/{id} → questão (lança ApiError 404 se não existir). Requer gestor. */
export function obterQuestao(id: number): Promise<Questao> {
  return apiFetch<Questao>(`/questoes/${id}`);
}

/** PATCH /questoes/{id} → edição parcial. 409 `questao_em_uso` se já usada em simulado. */
export function atualizarQuestao(id: number, patch: Partial<NovaQuestao>): Promise<Questao> {
  return apiFetch<Questao>(`/questoes/${id}`, { method: "PATCH", body: patch });
}

/** POST /questoes/import → importação em lote (cada item usa `etiquetas:{...}` aninhado). */
export function importarQuestoes(questoes: unknown[]): Promise<ResultadoImportacao> {
  return apiFetch<ResultadoImportacao>("/questoes/import", {
    method: "POST",
    body: { questoes },
  });
}
