import type { NavGrupo } from "./navGestao";

// Navegação do aluno (design_brief §4.2). Grupo único sem título.
export const navAluno: NavGrupo[] = [
  {
    titulo: "",
    itens: [
      { rotulo: "Início", para: "/app", icone: "dashboard", fim: true },
      { rotulo: "Meus simulados", para: "/app/simulados", icone: "simulados" },
      { rotulo: "Perfil", para: "/app/perfil", icone: "perfil" },
    ],
  },
];
