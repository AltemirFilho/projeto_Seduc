// Mapa de navegação da gestão (design_brief §4.3). Rotas batem com as do App.
export interface NavItem {
  rotulo: string;
  para: string;
  icone: string;
  /** NavLink `end` — ativo só na rota exata (usado no Dashboard). */
  fim?: boolean;
}

export interface NavGrupo {
  titulo: string;
  itens: NavItem[];
}

export const navGestao: NavGrupo[] = [
  {
    titulo: "Visão geral",
    itens: [{ rotulo: "Dashboard", para: "/gestao", icone: "dashboard", fim: true }],
  },
  {
    titulo: "Conteúdo",
    itens: [
      { rotulo: "Banco de questões", para: "/gestao/questoes", icone: "banco" },
      { rotulo: "Importar", para: "/gestao/importar", icone: "importar" },
    ],
  },
  {
    titulo: "Avaliações",
    itens: [
      { rotulo: "Simulados", para: "/gestao/simulados", icone: "simulados" },
      { rotulo: "Gerar prova", para: "/gestao/gerar-prova", icone: "prova" },
    ],
  },
  {
    titulo: "Pessoas",
    itens: [
      { rotulo: "Turmas", para: "/gestao/turmas", icone: "turmas" },
      { rotulo: "Usuários", para: "/gestao/usuarios", icone: "usuarios" },
    ],
  },
  {
    titulo: "Inteligência",
    itens: [
      { rotulo: "Relatórios", para: "/gestao/relatorios", icone: "relatorios" },
      { rotulo: "Diagnóstico (IA)", para: "/gestao/ia/diagnostico", icone: "diagnostico" },
      { rotulo: "Risco de evasão (IA)", para: "/gestao/ia/risco", icone: "risco" },
    ],
  },
  {
    titulo: "Conta",
    itens: [{ rotulo: "Perfil", para: "/gestao/perfil", icone: "perfil" }],
  },
];
