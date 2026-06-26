import { Card } from "../../components/clay";
import { t } from "../../i18n/pt-BR";

// Stub genérico para as telas da gestão ainda não construídas (mantém a navegação sem 404).
export function EmConstrucaoPage({ titulo, descricao }: { titulo: string; descricao?: string }) {
  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-text">{titulo}</h1>
      <Card className="mt-4">
        <p className="text-text-muted">{descricao ?? t.gestao.emConstrucao}</p>
      </Card>
    </div>
  );
}
