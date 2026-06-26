import { Link } from "react-router-dom";

import { Button, Card } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { t } from "../../i18n/pt-BR";

// A2 — Como funciona (design_brief §A2): passos numerados + cards por papel + FAQ.
const passos = [
  { titulo: t.comoFunciona.passo1Titulo, texto: t.comoFunciona.passo1Texto },
  { titulo: t.comoFunciona.passo2Titulo, texto: t.comoFunciona.passo2Texto },
  { titulo: t.comoFunciona.passo3Titulo, texto: t.comoFunciona.passo3Texto },
  { titulo: t.comoFunciona.passo4Titulo, texto: t.comoFunciona.passo4Texto },
];

export function ComoFuncionaPage() {
  return (
    <div className="space-y-12">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-bold text-text">{t.comoFunciona.titulo}</h1>
        <p className="mt-2 text-text-muted">{t.comoFunciona.sub}</p>
      </header>

      {/* Passos numerados */}
      <section>
        <h2 className="text-xl font-bold text-text mb-4">{t.comoFunciona.passosTitulo}</h2>
        <ol className="grid gap-4 sm:grid-cols-2">
          {passos.map((p, i) => (
            <Card key={p.titulo} className="flex gap-4">
              <span className="grid place-items-center h-10 w-10 shrink-0 rounded-full bg-primary text-on-primary font-display font-bold shadow-clay-sm">
                {i + 1}
              </span>
              <div>
                <h3 className="font-display font-bold text-text">{p.titulo}</h3>
                <p className="mt-1 text-sm text-text-muted">{p.texto}</p>
              </div>
            </Card>
          ))}
        </ol>
      </section>

      {/* Cards por papel */}
      <section>
        <h2 className="text-xl font-bold text-text mb-4">{t.comoFunciona.papeisTitulo}</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card>
            <div className="flex items-center gap-2">
              <Icon name="perfil" className="h-5 w-5 text-primary" />
              <h3 className="font-display font-bold text-text">{t.comoFunciona.papelAlunoTitulo}</h3>
            </div>
            <ul className="mt-3 space-y-2">
              {t.comoFunciona.papelAlunoItens.map((it) => (
                <li key={it} className="flex items-start gap-2 text-sm text-text-muted">
                  <Icon name="check" className="h-4 w-4 text-success mt-0.5 shrink-0" />
                  {it}
                </li>
              ))}
            </ul>
          </Card>
          <Card>
            <div className="flex items-center gap-2">
              <Icon name="dashboard" className="h-5 w-5 text-primary" />
              <h3 className="font-display font-bold text-text">{t.comoFunciona.papelGestaoTitulo}</h3>
            </div>
            <ul className="mt-3 space-y-2">
              {t.comoFunciona.papelGestaoItens.map((it) => (
                <li key={it} className="flex items-start gap-2 text-sm text-text-muted">
                  <Icon name="check" className="h-4 w-4 text-success mt-0.5 shrink-0" />
                  {it}
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </section>

      {/* FAQ */}
      <section>
        <h2 className="text-xl font-bold text-text mb-4">{t.comoFunciona.faqTitulo}</h2>
        <div className="space-y-3">
          {t.comoFunciona.faq.map((f) => (
            <details key={f.q} className="group bg-surface rounded-card shadow-clay-sm p-5">
              <summary className="flex items-center justify-between gap-3 cursor-pointer list-none font-display font-semibold text-text">
                {f.q}
                <Icon name="chevron" className="h-4 w-4 text-text-muted transition-transform group-open:rotate-180 shrink-0" />
              </summary>
              <p className="mt-2 text-sm text-text-muted">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      <div className="flex flex-wrap gap-3">
        <Link to="/login">
          <Button variante="primary">{t.comoFunciona.ctaEntrar}</Button>
        </Link>
        <Link to="/">
          <Button variante="secondary">{t.comoFunciona.voltar}</Button>
        </Link>
      </div>
    </div>
  );
}
