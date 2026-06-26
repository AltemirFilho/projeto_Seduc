import { Route, Routes } from "react-router-dom";

import { RequireAluno, RequireAuth, RequireGestao } from "./auth/guards";
import { AlunoLayout } from "./components/shell/AlunoLayout";
import { GestaoLayout } from "./components/shell/GestaoLayout";
import { PublicLayout } from "./components/shell/PublicLayout";
import { ComoFuncionaPage } from "./pages/public/ComoFuncionaPage";
import { LoginPage } from "./pages/public/LoginPage";
import { PortalPage } from "./pages/public/PortalPage";
import { AlunoInicioPage } from "./pages/app/AlunoInicioPage";
import { MeusSimuladosPage } from "./pages/app/MeusSimuladosPage";
import { PerfilAlunoPage } from "./pages/app/PerfilAlunoPage";
import { ResponderPage } from "./pages/app/ResponderPage";
import { ResultadoAlunoPage } from "./pages/app/ResultadoAlunoPage";
import { DashboardPage } from "./pages/gestao/DashboardPage";
import { GerarProvaPage } from "./pages/gestao/GerarProvaPage";
import { NovaQuestaoPage } from "./pages/gestao/NovaQuestaoPage";
import { QuestaoDetalhePage } from "./pages/gestao/QuestaoDetalhePage";
import { QuestoesPage } from "./pages/gestao/QuestoesPage";
import { NovoSimuladoPage } from "./pages/gestao/NovoSimuladoPage";
import { SimuladoDetalhePage } from "./pages/gestao/SimuladoDetalhePage";
import { SimuladosPage } from "./pages/gestao/SimuladosPage";
import { RelatoriosPage } from "./pages/gestao/RelatoriosPage";
import { DiagnosticoPage } from "./pages/gestao/DiagnosticoPage";
import { RiscoPage } from "./pages/gestao/RiscoPage";
import { UsuariosPage } from "./pages/gestao/UsuariosPage";
import { NovoUsuarioPage } from "./pages/gestao/NovoUsuarioPage";
import { EditarQuestaoPage } from "./pages/gestao/EditarQuestaoPage";
import { ImportarPage } from "./pages/gestao/ImportarPage";
import { TurmasPage } from "./pages/gestao/TurmasPage";
import { TurmaDetalhePage } from "./pages/gestao/TurmaDetalhePage";
import { PerfilGestaoPage } from "./pages/gestao/PerfilGestaoPage";
import { SemAcessoPage } from "./pages/SemAcessoPage";
import { NaoEncontradoPage } from "./pages/NaoEncontradoPage";

export function App() {
  return (
    <Routes>
      {/* Público */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<PortalPage />} />
        <Route path="/como-funciona" element={<ComoFuncionaPage />} />
      </Route>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/sem-acesso" element={<SemAcessoPage />} />

      {/* Autenticado */}
      <Route element={<RequireAuth />}>
        <Route element={<RequireAluno />}>
          <Route path="/app" element={<AlunoLayout />}>
            <Route index element={<AlunoInicioPage />} />
            <Route path="simulados" element={<MeusSimuladosPage />} />
            <Route path="simulados/:id/responder" element={<ResponderPage />} />
            <Route path="resultados/:id" element={<ResultadoAlunoPage />} />
            <Route path="perfil" element={<PerfilAlunoPage />} />
          </Route>
        </Route>

        <Route element={<RequireGestao />}>
          <Route path="/gestao" element={<GestaoLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="questoes" element={<QuestoesPage />} />
            <Route path="questoes/nova" element={<NovaQuestaoPage />} />
            <Route path="questoes/:id" element={<QuestaoDetalhePage />} />
            <Route path="questoes/:id/editar" element={<EditarQuestaoPage />} />
            <Route path="importar" element={<ImportarPage />} />
            <Route path="simulados" element={<SimuladosPage />} />
            <Route path="simulados/novo" element={<NovoSimuladoPage />} />
            <Route path="simulados/:id" element={<SimuladoDetalhePage />} />
            <Route path="gerar-prova" element={<GerarProvaPage />} />
            <Route path="turmas" element={<TurmasPage />} />
            <Route path="turmas/:id" element={<TurmaDetalhePage />} />
            <Route path="usuarios" element={<UsuariosPage />} />
            <Route path="usuarios/novo" element={<NovoUsuarioPage />} />
            <Route path="relatorios" element={<RelatoriosPage />} />
            <Route path="ia/diagnostico" element={<DiagnosticoPage />} />
            <Route path="ia/diagnostico/:simuladoId" element={<DiagnosticoPage />} />
            <Route path="ia/risco" element={<RiscoPage />} />
            <Route path="ia/risco/:alunoId" element={<RiscoPage />} />
            <Route path="perfil" element={<PerfilGestaoPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NaoEncontradoPage />} />
    </Routes>
  );
}
