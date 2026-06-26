import type {
  FinalizacaoSimulado,
  MeuResultado,
  Monitoramento,
  NovoSimulado,
  PreviewSimulado,
  RespostaSalva,
  SimuladoResumo,
} from "../../types/api";
import { apiFetch } from "./client";

export interface ListaSimulados {
  dados: SimuladoResumo[];
  meta: { total: number };
}

/** GET /simulados → lista (gestão; filtra por status/turma). Requer gestor. */
export function listarSimulados(
  filtro: { status?: string; turma_id?: number } = {},
): Promise<ListaSimulados> {
  const p = new URLSearchParams();
  if (filtro.status) p.set("status", filtro.status);
  if (filtro.turma_id != null) p.set("turma_id", String(filtro.turma_id));
  const q = p.toString();
  return apiFetch<ListaSimulados>(`/simulados${q ? `?${q}` : ""}`);
}

/** GET /simulados/disponiveis → simulados liberados/finalizados da turma do aluno logado. */
export function listarSimuladosDisponiveis(): Promise<ListaSimulados> {
  return apiFetch<ListaSimulados>("/simulados/disponiveis");
}

/** GET /simulados/{id} → resumo de um simulado. Requer gestor dono. */
export function obterSimulado(id: number): Promise<SimuladoResumo> {
  return apiFetch<SimuladoResumo>(`/simulados/${id}`);
}

/** GET /simulados/{id}/monitoramento → progresso ao vivo da turma. Requer gestor dono. */
export function monitorarSimulado(id: number): Promise<Monitoramento> {
  return apiFetch<Monitoramento>(`/simulados/${id}/monitoramento`);
}

/** POST /simulados → cria (status RASCUNHO). Requer gestor. */
export function criarSimulado(payload: NovoSimulado): Promise<SimuladoResumo> {
  return apiFetch<SimuladoResumo>("/simulados", { method: "POST", body: payload });
}

/** POST /simulados/{id}/gerar → sorteia e persiste as questões (status GERADO). */
export function gerarSimulado(id: number, seed?: number): Promise<SimuladoResumo> {
  return apiFetch<SimuladoResumo>(`/simulados/${id}/gerar`, {
    method: "POST",
    body: { seed: seed ?? null },
  });
}

/** GET /simulados/{id}/preview → questões COM gabarito (visão da gestão). */
export function previewSimulado(id: number): Promise<PreviewSimulado> {
  return apiFetch<PreviewSimulado>(`/simulados/${id}/preview`);
}

/** GET /simulados/{id}/questoes → questões SEM gabarito (visão do aluno). */
export function questoesDoAluno(id: number): Promise<PreviewSimulado> {
  return apiFetch<PreviewSimulado>(`/simulados/${id}/questoes`);
}

/** POST /respostas → autosave da resposta do aluno (identidade vem do token). */
export function salvarResposta(payload: {
  simulado_id: number;
  questao_id: number;
  alternativa_id: number;
}): Promise<RespostaSalva> {
  return apiFetch<RespostaSalva>("/respostas", { method: "POST", body: payload });
}

/** GET /simulados/{id}/meu-resultado → resultado individual (só FINALIZADO, senão 409). */
export function meuResultado(simuladoId: number): Promise<MeuResultado> {
  return apiFetch<MeuResultado>(`/simulados/${simuladoId}/meu-resultado`);
}

/** POST /simulados/{id}/liberar → status LIBERADO (só a partir de GERADO). */
export function liberarSimulado(id: number): Promise<SimuladoResumo> {
  return apiFetch<SimuladoResumo>(`/simulados/${id}/liberar`, { method: "POST" });
}

/** POST /simulados/{id}/finalizar → corrige e devolve resultados (só a partir de LIBERADO). */
export function finalizarSimulado(id: number): Promise<FinalizacaoSimulado> {
  return apiFetch<FinalizacaoSimulado>(`/simulados/${id}/finalizar`, { method: "POST" });
}

/** DELETE /simulados/{id}/questoes/{qid} → remove questão (só em GERADO). Devolve a prévia. */
export function removerQuestaoSimulado(id: number, questaoId: number): Promise<PreviewSimulado> {
  return apiFetch<PreviewSimulado>(`/simulados/${id}/questoes/${questaoId}`, { method: "DELETE" });
}

/** POST /simulados/{id}/questoes/{qid}/trocar → troca por equivalente (só em GERADO). Devolve a prévia. */
export function trocarQuestaoSimulado(id: number, questaoId: number): Promise<PreviewSimulado> {
  return apiFetch<PreviewSimulado>(`/simulados/${id}/questoes/${questaoId}/trocar`, {
    method: "POST",
  });
}
