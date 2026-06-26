import { Button, Card } from "../../components/clay";
import { useAuth } from "../../auth/AuthContext";
import { t } from "../../i18n/pt-BR";

// Perfil do aluno (GET /auth/me via contexto). Edição = [fase futura] (sem PATCH /usuarios/me).
export function PerfilAlunoPage() {
  const { usuario, sair } = useAuth();
  return (
    <div className="max-w-xl space-y-4">
      <h1 className="text-2xl font-bold text-text">{t.perfilAluno.titulo}</h1>
      <Card className="space-y-1">
        <Linha rotulo={t.perfilAluno.nome} valor={usuario?.nome} />
        <Linha rotulo={t.perfilAluno.email} valor={usuario?.email} />
        <Linha rotulo={t.perfilAluno.perfil} valor={usuario?.perfil} />
        <div className="pt-3">
          <Button variante="secondary" onClick={sair}>
            {t.comum.sair}
          </Button>
        </div>
      </Card>
    </div>
  );
}

function Linha({ rotulo, valor }: { rotulo: string; valor?: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-line py-2 last:border-0">
      <span className="text-text-muted text-sm">{rotulo}</span>
      <span className="text-text font-medium">{valor}</span>
    </div>
  );
}
