import { Button, Card } from "../../components/clay";
import { useAuth } from "../../auth/AuthContext";
import { t } from "../../i18n/pt-BR";

// C16 — Perfil da gestão (GET /auth/me via contexto). Edição = fase futura.
export function PerfilGestaoPage() {
  const { usuario, sair } = useAuth();
  return (
    <div className="max-w-xl space-y-4">
      <h1 className="text-2xl font-bold text-text">{t.perfilGestao.titulo}</h1>
      <Card className="space-y-1">
        <Linha rotulo={t.perfilGestao.nome} valor={usuario?.nome} />
        <Linha rotulo={t.perfilGestao.email} valor={usuario?.email} />
        <Linha rotulo={t.perfilGestao.perfil} valor={usuario?.perfil} />
      </Card>
      <p className="text-xs text-text-muted">{t.perfilGestao.edicaoFutura}</p>
      <Button variante="secondary" onClick={sair}>
        {t.comum.sair}
      </Button>
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
