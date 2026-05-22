"""Enums fechados (valores fixos, não gerenciáveis pelo Admin).

Diferente de Série/Matéria/Conteúdo/Nível — que são tabelas porque o Admin
pode editá-las — estes são valores de domínio que só mudam via código.
"""

import enum


class PerfilUsuario(enum.Enum):
    ADMIN = "admin"        # Secretaria — gerencia o banco de questões
    GESTOR = "gestor"      # Diretor/coordenador — cria e aplica simulados
    ALUNO = "aluno"        # Responde os simulados
    SUPORTE = "suporte"    # Professor/secretário — acompanha alunos


class StatusSimulado(enum.Enum):
    RASCUNHO = "rascunho"        # criado, ainda sem questões selecionadas
    GERADO = "gerado"            # questões selecionadas, aguardando liberação
    LIBERADO = "liberado"        # alunos já podem responder
    FINALIZADO = "finalizado"    # encerrado; notas calculadas
