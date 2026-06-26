// Tipos do contrato da API — refletem o backend real (não inventar campo/endpoint).
// Verdade de fio confirmada lendo app/api/routers/auth.py e batendo no endpoint.

export type Perfil = "admin" | "gestor" | "aluno" | "suporte";

/** Resposta de GET /auth/me e do campo `usuario` no login (objeto flat, não envelopado). */
export interface UsuarioOut {
  id: number;
  nome: string;
  email: string;
  perfil: Perfil;
}

/** Resposta de POST /auth/login (flat — NÃO usa o envelope {dados,meta}). */
export interface TokenOut {
  token: string;
  tipo: string; // "Bearer"
  expira_em_horas: number;
  usuario: UsuarioOut;
}

/** Metadados de paginação das listas. */
export interface Meta {
  pagina: number;
  porPagina: number;
  total: number;
  totalPaginas: number;
}

/** Envelope das listas paginadas: { dados: [...], meta: {...} }. */
export interface Envelope<T> {
  dados: T[];
  meta: Meta;
}

/** Corpo de erro de domínio do backend: { codigo, mensagem }. */
export interface ApiErro {
  codigo: string;
  mensagem: string;
  detalhes?: unknown;
}

// --- Domínio (shapes confirmados lendo os routers do backend) ---

export interface Alternativa {
  id: number;
  texto: string;
  correta: boolean;
  ordem_original: number;
}

/** GET /questoes → dados[]. serie/materia/conteudo/nivel vêm como nome (string). */
export interface Questao {
  id: number;
  enunciado: string;
  serie: string;
  materia: string;
  conteudo: string;
  nivel: string;
  adaptacoes: string[];
  alternativas: Alternativa[];
}

/** GET /turmas → lista flat (NÃO envelopada). */
export interface Turma {
  id: number;
  nome: string;
  ano_letivo: number;
  serie: string;
  escola: string;
}

/** GET /etiquetas/{series,materias,niveis} → lista flat [{id,nome}]. */
export interface Etiqueta {
  id: number;
  nome: string;
}

/** GET /etiquetas/conteudos → [{id,nome,materia}]. */
export interface Conteudo extends Etiqueta {
  materia: string;
}

// --- POST /questoes (criar) ---

export interface AlternativaIn {
  texto: string;
  correta: boolean;
}

export interface NovaQuestao {
  enunciado: string;
  serie: string;
  materia: string;
  conteudo: string;
  nivel: string;
  adaptacoes: string[];
  alternativas: AlternativaIn[];
}

// --- Simulados ---

export type StatusSimulado = "rascunho" | "gerado" | "liberado" | "finalizado";

/** Resposta de criar/gerar/liberar/listar/obter (_resumo do backend). */
export interface SimuladoResumo {
  id: number;
  titulo: string;
  status: StatusSimulado;
  turma_id: number;
  turma?: string | null; // nome da turma (ex.: "9A")
  gestor_id: number;
  total_questoes: number;
  criado_em?: string | null; // ISO 8601
  parametros: unknown;
}

export interface NovoSimulado {
  turma_id: number;
  titulo: string;
  serie: string;
  materia?: string;
  materias?: string[];
  conteudos?: string[];
  distribuicao?: Record<string, number>;
  quantidade: number;
  adaptacoes?: string[];
  seed?: number;
}

export interface AlternativaPreview {
  letra: string;
  texto: string;
  alternativa_id: number;
  correta?: boolean; // só na prévia com gabarito
}

export interface QuestaoPreview {
  ordem: number;
  questao_id: number;
  enunciado: string;
  conteudo: string;
  nivel: string;
  alternativas: AlternativaPreview[];
  gabarito?: string; // letra correta (só na prévia com gabarito)
}

export interface PreviewSimulado {
  simulado_id: number;
  questoes: QuestaoPreview[];
}

export interface ResultadoAluno {
  aluno_id: number;
  acertos: number;
  respondidas: number;
  total_questoes: number;
  nota: number;
}

export interface FinalizacaoSimulado {
  simulado_id: number;
  total_questoes: number;
  alunos_avaliados: number;
  resultados: ResultadoAluno[];
}

/** Resposta de POST /respostas (autosave do aluno). */
export interface RespostaSalva {
  salvo: boolean;
  resposta_id: number;
  questao_id: number;
  alternativa_id: number;
}

// --- Monitoramento de simulado (C9) ---

export type SituacaoMonitor = "concluido" | "em_andamento" | "nao_iniciou";

export interface MonitorAluno {
  aluno_id: number;
  nome: string;
  respondidas: number;
  total: number;
  situacao: SituacaoMonitor;
}

/** GET /simulados/{id}/monitoramento → progresso ao vivo da turma (derivado das respostas). */
export interface Monitoramento {
  simulado_id: number;
  status: StatusSimulado;
  total_questoes: number;
  total_alunos: number;
  concluidos: number;
  em_andamento: number;
  nao_iniciaram: number;
  por_aluno: MonitorAluno[];
}

// --- Relatórios (C13) ---

export interface ConteudoErro {
  conteudo: string;
  total: number;
  erros: number;
  taxa_erro: number; // 0..1
}

export interface RelatorioTurma {
  turma_id: number;
  turma: string;
  alunos: number;
  simulados_corrigidos: number;
  media_turma: number; // 0..10
  conteudos: ConteudoErro[]; // pior primeiro
}

// --- Resultado do aluno (B4) ---

export interface QuestaoResultado {
  ordem: number;
  questao_id: number;
  enunciado: string;
  conteudo: string;
  sua_resposta: string | null; // letra
  gabarito: string; // letra
  acertou: boolean | null;
}

export interface MeuResultado {
  simulado_id: number;
  aluno_id: number;
  nota: number; // 0..10
  acertos: number;
  total_questoes: number;
  questoes: QuestaoResultado[];
}

// --- IA (Frente B) ---

export type ClassificacaoRisco = "baixo" | "medio" | "alto" | "indeterminado";

export interface Risco {
  aluno_id: number;
  score_risco: number; // 0..1
  classificacao: ClassificacaoRisco;
  fatores: string[];
  modelo_versao: string;
  calculada_em: string | null;
}

export interface Diagnostico {
  simulado_id: number;
  resumo: string;
  pontos_fracos: string[];
  recomendacoes: string[];
  modelo_versao: string; // "indisponivel" = fallback sem IA
  gerado_em: string | null;
}

// --- Usuários (C12) ---

export interface Usuario {
  id: number;
  /** id da entidade Aluno (≠ usuario.id) — usado em /ia/risco/{aluno_id}; null se não for aluno. */
  aluno_id: number | null;
  nome: string;
  email: string;
  perfil: Perfil;
  turma_id: number | null;
}

export interface NovoUsuario {
  nome: string;
  email: string;
  senha: string;
  perfil: Perfil;
  turma_id?: number | null;
}

// --- Importação em lote ---

export interface ResultadoImportacao {
  importadas: number;
  rejeitadas: number;
  erros: { linha: number; motivo: string }[];
}

// --- Gerar prova (C5) ---

export interface AlternativaProva {
  letra: string;
  texto: string;
  alternativa_id: number;
}

export interface QuestaoProva {
  ordem: number;
  questao_id: number;
  enunciado: string;
  materia: string;
  conteudo: string;
  nivel: string;
  alternativas: AlternativaProva[];
}

export interface GerarProvaParams {
  serie: string;
  materia?: string;
  materias?: string[];
  conteudos?: string[];
  distribuicao?: Record<string, number>; // proporção por nível (0..1)
  quantidade: number;
  adaptacoes?: string[];
  seed?: number;
}

export interface ProvaGerada {
  serie: string;
  materias: string[];
  total: number;
  distribuicao_real: Record<string, number>; // contagem por nível
  questoes: QuestaoProva[];
  gabarito: Record<string, string>; // ordem(string) -> letra correta
}
