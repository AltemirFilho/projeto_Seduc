import { Link, NavLink, Outlet } from "react-router-dom";

import { Button } from "../clay";
import { t } from "../../i18n/pt-BR";

// Shell público (design_brief §4.1): topbar (logo + nav + Entrar) + conteúdo + rodapé institucional.
export function PublicLayout() {
  const navClass = ({ isActive }: { isActive: boolean }) =>
    "text-sm font-medium transition-colors " +
    (isActive ? "text-primary" : "text-text-muted hover:text-text");

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <header className="sticky top-0 z-20 bg-bg/85 backdrop-blur border-b border-line">
        <div className="mx-auto w-full max-w-5xl flex items-center gap-4 h-16 px-4 sm:px-6">
          <Link to="/" className="font-display font-bold text-text">
            {t.app.nome}
          </Link>
          <nav className="ml-auto flex items-center gap-5">
            <NavLink to="/" end className={navClass}>
              {t.publico.inicio}
            </NavLink>
            <NavLink to="/como-funciona" className={navClass}>
              {t.publico.comoFunciona}
            </NavLink>
            <Link to="/login">
              <Button variante="primary" tamanho="sm">
                {t.publico.entrar}
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto w-full max-w-5xl px-4 sm:px-6 py-8 sm:py-12">
          <Outlet />
        </div>
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto w-full max-w-5xl px-4 sm:px-6 py-6 text-sm text-text-muted">
          <p className="font-medium text-text">{t.marca.rodape}</p>
          <p className="mt-1">{t.publico.rodapeNota}</p>
        </div>
      </footer>
    </div>
  );
}
