import type { Conteudo, Etiqueta } from "../../types/api";
import { apiFetch } from "./client";

// GET /etiquetas/* → listas flat. Requer apenas autenticação (qualquer perfil).
export const listarSeries = (): Promise<Etiqueta[]> => apiFetch<Etiqueta[]>("/etiquetas/series");
export const listarMaterias = (): Promise<Etiqueta[]> => apiFetch<Etiqueta[]>("/etiquetas/materias");
export const listarNiveis = (): Promise<Etiqueta[]> => apiFetch<Etiqueta[]>("/etiquetas/niveis");

export function listarConteudos(materia?: string): Promise<Conteudo[]> {
  const q = materia ? `?materia=${encodeURIComponent(materia)}` : "";
  return apiFetch<Conteudo[]>(`/etiquetas/conteudos${q}`);
}
