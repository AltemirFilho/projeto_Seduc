import { Link } from "react-router-dom";

import { Button, Card } from "../components/clay";
import { t } from "../i18n/pt-BR";

export function NaoEncontradoPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-bg">
      <Card className="w-full max-w-md text-center">
        <div className="font-display text-5xl font-bold text-primary">404</div>
        <h1 className="mt-2 text-2xl font-bold text-text">{t.naoEncontrado.titulo}</h1>
        <p className="mt-2 text-text-muted">{t.naoEncontrado.texto}</p>
        <div className="mt-6 flex justify-center">
          <Link to="/">
            <Button variante="secondary">{t.comum.voltarInicio}</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
