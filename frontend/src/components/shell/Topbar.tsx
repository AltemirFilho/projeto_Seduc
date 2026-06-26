import { useAuth } from "../../auth/AuthContext";
import { t } from "../../i18n/pt-BR";
import { Icon } from "./icons";

function iniciaisDe(nome: string): string {
  return nome
    .trim()
    .split(/\s+/)
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function Topbar({ aoAbrirMenu, busca = true }: { aoAbrirMenu: () => void; busca?: boolean }) {
  const { usuario, sair } = useAuth();

  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 h-16 px-4 lg:px-8 bg-bg/85 backdrop-blur border-b border-line">
      <button className="lg:hidden p-2 -ml-2 text-text" onClick={aoAbrirMenu} aria-label="Abrir menu">
        <Icon name="menu" />
      </button>

      {/* Busca global — visual por enquanto. TODO: ligar busca quando houver endpoint. */}
      {busca && (
        <div className="relative flex-1 max-w-md hidden sm:block">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
            <Icon name="busca" className="h-4 w-4" />
          </span>
          <input
            type="search"
            aria-label={t.gestao.buscar}
            placeholder={t.gestao.buscarPlaceholder}
            className="w-full h-10 pl-9 pr-3 rounded-input bg-surface-sunken text-text placeholder:text-text-muted/70 shadow-clay-inset focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          />
        </div>
      )}

      <div className="flex-1" />

      <button
        className="p-2 rounded-full text-text-muted hover:bg-surface-sunken"
        aria-label={t.gestao.notificacoes}
      >
        <Icon name="sino" />
      </button>

      <div className="flex items-center gap-3">
        <div className="hidden sm:block text-right leading-tight">
          <p className="text-sm font-semibold text-text truncate max-w-[160px]">{usuario?.nome}</p>
          <p className="text-xs text-text-muted">{usuario?.perfil}</p>
        </div>
        <div className="grid place-items-center h-10 w-10 rounded-full bg-primary text-on-primary font-display font-bold text-sm shadow-clay-sm">
          {iniciaisDe(usuario?.nome ?? "?")}
        </div>
        <button
          onClick={sair}
          className="p-2 rounded-full text-text-muted hover:bg-surface-sunken"
          aria-label={t.comum.sair}
          title={t.comum.sair}
        >
          <Icon name="sair" />
        </button>
      </div>
    </header>
  );
}
