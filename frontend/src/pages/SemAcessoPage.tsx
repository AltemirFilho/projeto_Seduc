import { Link } from "react-router-dom";

import { Button, Card } from "../components/clay";
import { t } from "../i18n/pt-BR";

// Tela 403 "sem acesso": logado, mas sem o perfil exigido pela rota.
export function SemAcessoPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-bg">
      <Card className="w-full max-w-md text-center">
        <div className="font-display text-5xl font-bold text-accent">403</div>
        <h1 className="mt-2 text-2xl font-bold text-text">{t.semAcesso.titulo}</h1>
        <p className="mt-2 text-text-muted">{t.semAcesso.texto}</p>
        <div className="mt-6 flex justify-center">
          <Link to="/">
            <Button variante="secondary">{t.comum.voltarInicio}</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
