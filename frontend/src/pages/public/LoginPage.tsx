import { useEffect, useRef, useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { Button, Card, Field, Input } from "../../components/clay";
import { useAuth } from "../../auth/AuthContext";
import { rotaInicialPorPerfil } from "../../auth/perfil";
import { ApiError } from "../../lib/api/client";
import { login } from "../../lib/api/auth";
import { t } from "../../i18n/pt-BR";

interface LocationState {
  de?: string;
}

export function LoginPage() {
  const { autenticado, usuario, entrar } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const emailRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    emailRef.current?.focus();
  }, []);

  const mutation = useMutation({
    mutationFn: () => login(email.trim(), senha),
    onSuccess: (res) => {
      entrar(res.token, res.usuario);
      const de = (location.state as LocationState | null)?.de;
      navigate(de ?? rotaInicialPorPerfil(res.usuario.perfil), { replace: true });
    },
  });

  // Já logado: não mostrar o login, mandar pra home do perfil.
  if (autenticado && usuario) {
    return <Navigate to={rotaInicialPorPerfil(usuario.perfil)} replace />;
  }

  // Qualquer 403 no login = "e-mail ou senha inválidos" (não revelar qual campo).
  const mensagemErro = (() => {
    const e = mutation.error;
    if (!e) return null;
    if (e instanceof ApiError) {
      if (e.status === 0) return t.login.erroRede;
      if (e.status === 403) return t.login.erroCredenciais;
      return e.message || t.login.erroCredenciais;
    }
    return t.login.erroCredenciais;
  })();

  function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    if (!email || !senha || mutation.isPending) return;
    mutation.mutate();
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Painel de marca (deep blue) — some no mobile */}
      <aside className="hidden lg:flex flex-col justify-between bg-primary text-on-primary p-12">
        <div className="font-display text-2xl font-bold">{t.app.nome}</div>
        <div className="max-w-md">
          <h1 className="text-on-primary text-4xl font-bold leading-tight">{t.marca.frase}</h1>
          <p className="mt-4 text-on-primary/80 text-lg">{t.app.tagline}</p>
        </div>
        <div className="text-on-primary/60 text-sm">{t.marca.rodape}</div>
      </aside>

      {/* Card de login */}
      <main className="flex items-center justify-center min-h-screen p-6 bg-bg">
        <Card className="w-full max-w-md">
          <div className="lg:hidden font-display text-xl font-bold text-primary mb-6">{t.app.nome}</div>

          <h2 className="text-2xl font-bold text-text">{t.login.titulo}</h2>
          <p className="mt-1 text-text-muted">{t.login.subtitulo}</p>

          <form onSubmit={onSubmit} className="mt-6 flex flex-col gap-4" noValidate>
            <Field label={t.login.email} htmlFor="email">
              <Input
                ref={emailRef}
                id="email"
                name="email"
                type="email"
                inputMode="email"
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t.login.placeholderEmail}
                invalido={mensagemErro !== null}
              />
            </Field>

            <Field label={t.login.senha} htmlFor="senha" erro={mensagemErro ?? undefined}>
              <Input
                id="senha"
                name="senha"
                type="password"
                autoComplete="current-password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                placeholder={t.login.placeholderSenha}
                invalido={mensagemErro !== null}
                aria-describedby={mensagemErro ? "senha-erro" : undefined}
              />
            </Field>

            <Button
              type="submit"
              variante="primary"
              tamanho="lg"
              blocoCompleto
              carregando={mutation.isPending}
              disabled={!email || !senha}
            >
              {mutation.isPending ? t.login.entrando : t.login.entrar}
            </Button>

            {/* esqueci a senha = [fase futura] — sem endpoint de reset ainda */}
            <button
              type="button"
              disabled
              title={t.login.esqueciIndisponivel}
              className="text-sm text-text-muted/70 cursor-not-allowed self-center mt-1"
            >
              {t.login.esqueci}
            </button>
          </form>
        </Card>
      </main>
    </div>
  );
}
