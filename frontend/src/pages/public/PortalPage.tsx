import { Link } from "react-router-dom";

import { Button, Card, StatCard } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { t } from "../../i18n/pt-BR";

// A1 — Portal público (design_brief §A1): hero + StatCards (exemplo) + acesso rápido + destaques.
const acessos = [
  { icon: "perfil", titulo: t.portal.acessoAlunoTitulo, texto: t.portal.acessoAlunoTexto, to: "/login" },
  { icon: "dashboard", titulo: t.portal.acessoGestaoTitulo, texto: t.portal.acessoGestaoTexto, to: "/login" },
  { icon: "diagnostico", titulo: t.portal.acessoComoTitulo, texto: t.portal.acessoComoTexto, to: "/como-funciona" },
];

const destaques = [
  { icon: "banco", titulo: t.portal.destaque1Titulo, texto: t.portal.destaque1Texto },
  { icon: "prova", titulo: t.portal.destaque2Titulo, texto: t.portal.destaque2Texto },
  { icon: "diagnostico", titulo: t.portal.destaque3Titulo, texto: t.portal.destaque3Texto },
];

export function PortalPage() {
  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center max-w-2xl mx-auto">
        <p className="font-display text-sm font-semibold tracking-wide text-accent-ink">{t.portal.badge}</p>
        <h1 className="mt-3 text-3xl sm:text-4xl font-bold text-text">{t.marca.frase}</h1>
        <p className="mt-3 text-text-muted">{t.app.tagline}</p>
        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Link to="/login">
            <Button variante="primary" tamanho="lg">
              {t.portal.ctaEntrar}
            </Button>
          </Link>
          <Link to="/como-funciona">
            <Button variante="secondary" tamanho="lg">
              {t.portal.ctaComoFunciona}
            </Button>
          </Link>
        </div>
      </section>

      {/* StatCards (números ilustrativos) */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard cor="primary" exemplo icone={<Icon name="simulados" />} rotulo={t.portal.statSimulados} valor={t.portal.statSimuladosValor} />
        <StatCard cor="secondary" exemplo icone={<Icon name="banco" />} rotulo={t.portal.statQuestoes} valor={t.portal.statQuestoesValor} />
        <StatCard cor="accent" exemplo icone={<Icon name="turmas" />} rotulo={t.portal.statEscolas} valor={t.portal.statEscolasValor} />
        <StatCard cor="success" exemplo icone={<Icon name="usuarios" />} rotulo={t.portal.statAlunos} valor={t.portal.statAlunosValor} />
      </section>

      {/* Acesso rápido */}
      <section>
        <h2 className="text-xl font-bold text-text mb-4">{t.portal.acessoTitulo}</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {acessos.map((c) => (
            <Card key={c.titulo} className="flex flex-col">
              <div className="grid place-items-center h-11 w-11 rounded-2xl bg-secondary text-secondary-ink shadow-clay-sm">
                <Icon name={c.icon} />
              </div>
              <h3 className="mt-3 font-display font-bold text-text">{c.titulo}</h3>
              <p className="mt-1 text-sm text-text-muted flex-1">{c.texto}</p>
              <Link to={c.to} className="mt-3 text-primary font-semibold text-sm hover:underline">
                {t.portal.acessar} →
              </Link>
            </Card>
          ))}
        </div>
      </section>

      {/* Destaques */}
      <section>
        <h2 className="text-xl font-bold text-text mb-4">{t.portal.destaquesTitulo}</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {destaques.map((d) => (
            <Card key={d.titulo}>
              <div className="grid place-items-center h-11 w-11 rounded-2xl bg-accent/15 text-accent-ink shadow-clay-sm">
                <Icon name={d.icon} />
              </div>
              <h3 className="mt-3 font-display font-bold text-text">{d.titulo}</h3>
              <p className="mt-1 text-sm text-text-muted">{d.texto}</p>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
