import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { Button, Card, Field, Input, Select } from "../../components/clay";
import { ApiError } from "../../lib/api/client";
import { listarTurmas } from "../../lib/api/turmas";
import { criarUsuario } from "../../lib/api/usuarios";
import type { Perfil } from "../../types/api";
import { t } from "../../i18n/pt-BR";

// C12 — Cadastrar usuário. POST /usuarios (aluno exige turma_id).
export function NovoUsuarioPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [perfil, setPerfil] = useState<Perfil>("aluno");
  const [turmaId, setTurmaId] = useState("");
  const [erroValidacao, setErroValidacao] = useState<string | null>(null);

  const turmas = useQuery({ queryKey: ["turmas"], queryFn: listarTurmas });

  const mutation = useMutation({
    mutationFn: () =>
      criarUsuario({
        nome: nome.trim(),
        email: email.trim(),
        senha,
        perfil,
        turma_id: perfil === "aluno" ? Number(turmaId) : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      navigate("/gestao/usuarios");
    },
  });

  function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    if (!nome.trim() || !email.trim() || senha.length < 6) {
      setErroValidacao(t.usuarios.erroCampos);
      return;
    }
    if (perfil === "aluno" && !turmaId) {
      setErroValidacao(t.usuarios.erroAlunoTurma);
      return;
    }
    setErroValidacao(null);
    mutation.mutate();
  }

  const erroServidor = mutation.error
    ? mutation.error instanceof ApiError
      ? mutation.error.message || t.usuarios.erroSalvar
      : t.usuarios.erroSalvar
    : null;
  const erro = erroValidacao ?? erroServidor;

  return (
    <form onSubmit={onSubmit} className="space-y-5 max-w-xl" noValidate>
      <h1 className="text-2xl font-bold text-text">{t.usuarios.novo}</h1>

      <Card className="space-y-4">
        <Field label={t.usuarios.nome} htmlFor="nome">
          <Input id="nome" value={nome} onChange={(e) => setNome(e.target.value)} />
        </Field>
        <Field label={t.usuarios.email} htmlFor="email">
          <Input id="email" type="email" autoComplete="off" value={email} onChange={(e) => setEmail(e.target.value)} />
        </Field>
        <Field label={t.usuarios.senha} htmlFor="senha">
          <Input id="senha" type="password" autoComplete="new-password" value={senha} onChange={(e) => setSenha(e.target.value)} />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label={t.usuarios.perfil} htmlFor="perfil">
            <Select id="perfil" value={perfil} onChange={(e) => setPerfil(e.target.value as Perfil)}>
              <option value="aluno">aluno</option>
              <option value="gestor">gestor</option>
              <option value="admin">admin</option>
              <option value="suporte">suporte</option>
            </Select>
          </Field>

          {perfil === "aluno" && (
            <Field label={t.usuarios.turma} htmlFor="turma">
              <Select id="turma" value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
                <option value="">{t.usuarios.selecioneTurma}</option>
                {turmas.data?.map((tm) => (
                  <option key={tm.id} value={tm.id}>
                    {tm.nome} — {tm.serie}
                  </option>
                ))}
              </Select>
            </Field>
          )}
        </div>
      </Card>

      {erro && (
        <p role="alert" className="text-danger text-sm">
          {erro}
        </p>
      )}

      <div className="flex gap-3">
        <Button type="submit" variante="primary" carregando={mutation.isPending}>
          {mutation.isPending ? t.usuarios.salvando : t.usuarios.salvar}
        </Button>
        <Button type="button" variante="ghost" onClick={() => navigate("/gestao/usuarios")}>
          {t.usuarios.cancelar}
        </Button>
      </div>
    </form>
  );
}
