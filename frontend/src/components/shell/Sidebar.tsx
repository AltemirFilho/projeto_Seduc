import { NavLink } from "react-router-dom";

import { t } from "../../i18n/pt-BR";
import { Icon } from "./icons";
import type { NavGrupo } from "./navGestao";

interface Props {
  grupos: NavGrupo[];
  aberto: boolean;
  aoFechar: () => void;
}

// Sidebar clay deep-blue genérica (gestão e aluno). Estática em ≥lg; drawer com overlay no mobile.
export function Sidebar({ grupos, aberto, aoFechar }: Props) {
  return (
    <>
      {aberto && (
        <div
          className="fixed inset-0 z-30 bg-primary/40 backdrop-blur-sm lg:hidden"
          onClick={aoFechar}
          aria-hidden="true"
        />
      )}

      <aside
        className={
          "fixed inset-y-0 left-0 z-40 w-[280px] bg-primary text-on-primary flex flex-col " +
          "transition-transform duration-200 lg:static lg:translate-x-0 " +
          (aberto ? "translate-x-0" : "-translate-x-full")
        }
      >
        <div className="flex items-center justify-between px-6 h-16 shrink-0">
          <span className="font-display text-lg font-bold">{t.app.nome}</span>
          <button
            className="lg:hidden p-2 -mr-2 text-on-primary/80 hover:text-on-primary"
            onClick={aoFechar}
            aria-label="Fechar menu"
          >
            <Icon name="fechar" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-6 space-y-5">
          {grupos.map((grupo, gi) => (
            <div key={grupo.titulo || gi}>
              {grupo.titulo && (
                <p className="px-3 mb-1 text-xs font-semibold uppercase tracking-wider text-on-primary/50">
                  {grupo.titulo}
                </p>
              )}
              <ul className="space-y-1">
                {grupo.itens.map((item) => (
                  <li key={item.para}>
                    <NavLink
                      to={item.para}
                      end={item.fim}
                      onClick={aoFechar}
                      className={({ isActive }) =>
                        "flex items-center gap-3 rounded-btn px-3 py-2.5 text-sm font-medium transition-colors " +
                        (isActive
                          ? "bg-secondary text-secondary-ink shadow-[0_3px_8px_-2px_rgba(0,0,0,0.25)]"
                          : "text-on-primary/80 hover:bg-primary-hover hover:text-on-primary")
                      }
                    >
                      <Icon name={item.icone} className="h-5 w-5 shrink-0" />
                      <span className="truncate">{item.rotulo}</span>
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
      </aside>
    </>
  );
}
