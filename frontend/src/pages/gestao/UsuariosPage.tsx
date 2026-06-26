import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Button, Card, Select, Skeleton } from "../../components/clay";
import { Icon } from "../../components/shell/icons";
import { listarUsuarios } from "../../lib/api/usuarios";
import { t } from "../../i18n/pt-BR";

// C12 — Listar usuários (filtro por perfil). Requer gestor.
export function UsuariosPage() {
  const [perfil, setPerfil] = useState("");
  const query = useQuery({
    queryKey: ["usuarios", perfil],
    queryFn: () => listarUsuarios({ perfil: perfil || undefined }),
  });
  const dados = query.data?.dados ?? [];

  return (
    <div className="space-y-5 max-w-4xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-text">{t.usuarios.titulo}</h1>
          {query.data && <p className="text-sm text-text-muted">{t.usuarios.total(query.data.meta.total)}</p>}
        </div>
        <Link to="/gestao/usuarios/novo">
          <Button variante="primary" tamanho="sm">
            <Icon name="usuarios" className="h-4 w-4" />
            {t.usuarios.novo}
          </Button>
        </Link>
      </div>

      <Card className="p-4 max-w-xs">
        <Select value={perfil} onChange={(e) => setPerfil(e.target.value)} aria-label={t.usuarios.colPerfil}>
          <option value="">{t.usuarios.filtroPerfil}</option>
          <option value="aluno">aluno</option>
          <option value="gestor">gestor</option>
          <option value="admin">admin</option>
          <option value="suporte">suporte</option>
        </Select>
      </Card>

      {query.isLoading ? (
        <Card>
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        </Card>
      ) : query.isError ? (
        <Card>
          <p className="text-danger">{t.usuarios.erro}</p>
        </Card>
      ) : dados.length === 0 ? (
        <Card>
          <p className="text-text-muted text-center py-6">{t.usuarios.vazio}</p>
        </Card>
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-text-muted">
                  <th className="px-5 py-3 font-semibold">{t.usuarios.colNome}</th>
                  <th className="px-3 py-3 font-semibold">{t.usuarios.colEmail}</th>
                  <th className="px-3 py-3 font-semibold">{t.usuarios.colPerfil}</th>
                  <th className="px-5 py-3 font-semibold">{t.usuarios.colTurma}</th>
                </tr>
              </thead>
              <tbody>
                {dados.map((u) => (
                  <tr key={u.id} className="border-t border-line">
                    <td className="px-5 py-3 text-text whitespace-nowrap">{u.nome}</td>
                    <td className="px-3 py-3 text-text-muted">{u.email}</td>
                    <td className="px-3 py-3">
                      <span className="px-2 py-0.5 rounded-chip bg-secondary/40 text-secondary-ink text-xs font-medium">
                        {u.perfil}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-text-muted">{u.turma_id ?? t.usuarios.semTurma}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
