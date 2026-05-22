from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import PerfilUsuario, StatusSimulado


# ---------------- ETIQUETAS ----------------


class Serie(Base):
    """Série/ano escolar. Ex.: '6º ano', '9º ano', '3ª série EM'."""

    __tablename__ = "series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)

    questoes: Mapped[List["Questao"]] = relationship(back_populates="serie")

    def __repr__(self) -> str:
        return f"Serie(id={self.id}, nome={self.nome!r})"


class Materia(Base):
    """Disciplina. Ex.: 'Matemática', 'Português', 'Ciências'."""

    __tablename__ = "materias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    conteudos: Mapped[List["Conteudo"]] = relationship(
        back_populates="materia",
        cascade="all, delete-orphan",
    )
    questoes: Mapped[List["Questao"]] = relationship(back_populates="materia")

    def __repr__(self) -> str:
        return f"Materia(id={self.id}, nome={self.nome!r})"


class Conteudo(Base):
    """Tópico dentro de uma matéria. Ex.: 'Equação do 1º grau' em Matemática."""

    __tablename__ = "conteudos"
    __table_args__ = (
        UniqueConstraint("nome", "materia_id", name="uq_conteudo_nome_materia"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id", ondelete="CASCADE"),
        nullable=False,
    )

    materia: Mapped["Materia"] = relationship(back_populates="conteudos")
    questoes: Mapped[List["Questao"]] = relationship(back_populates="conteudo")

    def __repr__(self) -> str:
        return f"Conteudo(id={self.id}, nome={self.nome!r}, materia_id={self.materia_id})"


class Nivel(Base):
    """Dificuldade. Ex.: 'Fácil', 'Médio', 'Difícil'."""

    __tablename__ = "niveis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    questoes: Mapped[List["Questao"]] = relationship(back_populates="nivel")

    def __repr__(self) -> str:
        return f"Nivel(id={self.id}, nome={self.nome!r})"


# ---------------- BLOCO QUESTÃO ----------------


class Questao(Base):
    __tablename__ = "questoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enunciado: Mapped[str] = mapped_column(Text, nullable=False)
    imagem_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    serie_id: Mapped[int] = mapped_column(ForeignKey("series.id"), nullable=False)
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id"), nullable=False)
    conteudo_id: Mapped[int] = mapped_column(ForeignKey("conteudos.id"), nullable=False)
    nivel_id: Mapped[int] = mapped_column(ForeignKey("niveis.id"), nullable=False)

    # Lista de strings, ex.: ["tdah", "dislexia"]. SQLite armazena como TEXT;
    # no PostgreSQL vira JSONB sem mexer no código (SQLAlchemy abstrai).
    adaptacoes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    serie: Mapped["Serie"] = relationship(back_populates="questoes")
    materia: Mapped["Materia"] = relationship(back_populates="questoes")
    conteudo: Mapped["Conteudo"] = relationship(back_populates="questoes")
    nivel: Mapped["Nivel"] = relationship(back_populates="questoes")

    alternativas: Mapped[List["Alternativa"]] = relationship(
        back_populates="questao",
        cascade="all, delete-orphan",
        order_by="Alternativa.ordem_original",
    )

    def __repr__(self) -> str:
        return (
            f"Questao(id={self.id}, materia_id={self.materia_id}, "
            f"conteudo_id={self.conteudo_id}, nivel_id={self.nivel_id})"
        )


class Alternativa(Base):
    __tablename__ = "alternativas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    questao_id: Mapped[int] = mapped_column(
        ForeignKey("questoes.id", ondelete="CASCADE"),
        nullable=False,
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    correta: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ordem_original: Mapped[int] = mapped_column(Integer, nullable=False)

    questao: Mapped["Questao"] = relationship(back_populates="alternativas")

    def __repr__(self) -> str:
        return (
            f"Alternativa(id={self.id}, questao_id={self.questao_id}, "
            f"correta={self.correta})"
        )


# ---------------- USUÁRIOS E ESTRUTURA ESCOLAR ----------------


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(SAEnum(PerfilUsuario), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    aluno: Mapped[Optional["Aluno"]] = relationship(
        back_populates="usuario", uselist=False
    )

    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, email={self.email!r}, perfil={self.perfil.value})"


class Escola(Base):
    __tablename__ = "escolas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    municipio: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    codigo_inep: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)

    turmas: Mapped[List["Turma"]] = relationship(
        back_populates="escola", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Escola(id={self.id}, nome={self.nome!r})"


class Turma(Base):
    __tablename__ = "turmas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    escola_id: Mapped[int] = mapped_column(ForeignKey("escolas.id"), nullable=False)
    serie_id: Mapped[int] = mapped_column(ForeignKey("series.id"), nullable=False)
    ano_letivo: Mapped[int] = mapped_column(Integer, nullable=False)
    nome: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)  # ex.: "9A"

    escola: Mapped["Escola"] = relationship(back_populates="turmas")
    serie: Mapped["Serie"] = relationship()
    alunos: Mapped[List["Aluno"]] = relationship(back_populates="turma")
    simulados: Mapped[List["Simulado"]] = relationship(back_populates="turma")

    def __repr__(self) -> str:
        return f"Turma(id={self.id}, nome={self.nome!r}, ano_letivo={self.ano_letivo})"


class Aluno(Base):
    __tablename__ = "alunos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), unique=True, nullable=False
    )
    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id"), nullable=False)
    # Adaptações cognitivas do aluno, ex.: ["tdah", "dislexia"]
    perfil_cognitivo: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="aluno")
    turma: Mapped["Turma"] = relationship(back_populates="alunos")
    respostas: Mapped[List["Resposta"]] = relationship(back_populates="aluno")

    def __repr__(self) -> str:
        return f"Aluno(id={self.id}, usuario_id={self.usuario_id}, turma_id={self.turma_id})"


# ---------------- SIMULADOS E RESPOSTAS ----------------


class Simulado(Base):
    __tablename__ = "simulados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gestor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(160), nullable=False)
    # Parâmetros usados na geração (série, matéria, distribuição, etc.)
    parametros_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[StatusSimulado] = mapped_column(
        SAEnum(StatusSimulado), default=StatusSimulado.RASCUNHO, nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    gestor: Mapped["Usuario"] = relationship()
    turma: Mapped["Turma"] = relationship(back_populates="simulados")
    questoes: Mapped[List["SimuladoQuestao"]] = relationship(
        back_populates="simulado",
        cascade="all, delete-orphan",
        order_by="SimuladoQuestao.ordem_questao",
    )
    respostas: Mapped[List["Resposta"]] = relationship(back_populates="simulado")

    def __repr__(self) -> str:
        return f"Simulado(id={self.id}, titulo={self.titulo!r}, status={self.status.value})"


class SimuladoQuestao(Base):
    """Liga uma questão a um simulado e congela a ordem das alternativas.

    `alternativas_ordem` é a sequência de alternativa_id sorteada para esta
    aplicação. Assim a ordem é embaralhada por simulado SEM desvincular a
    alternativa do seu cabeçalho (a fonte da verdade continua na tabela
    alternativas).
    """

    __tablename__ = "simulado_questoes"
    __table_args__ = (
        UniqueConstraint("simulado_id", "questao_id", name="uq_simulado_questao"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulado_id: Mapped[int] = mapped_column(
        ForeignKey("simulados.id", ondelete="CASCADE"), nullable=False
    )
    questao_id: Mapped[int] = mapped_column(ForeignKey("questoes.id"), nullable=False)
    ordem_questao: Mapped[int] = mapped_column(Integer, nullable=False)
    alternativas_ordem: Mapped[list] = mapped_column(JSON, nullable=False)

    simulado: Mapped["Simulado"] = relationship(back_populates="questoes")
    questao: Mapped["Questao"] = relationship()

    def __repr__(self) -> str:
        return (
            f"SimuladoQuestao(simulado_id={self.simulado_id}, "
            f"questao_id={self.questao_id}, ordem={self.ordem_questao})"
        )


class Resposta(Base):
    __tablename__ = "respostas"
    __table_args__ = (
        UniqueConstraint(
            "aluno_id", "simulado_id", "questao_id", name="uq_resposta_unica"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), nullable=False)
    simulado_id: Mapped[int] = mapped_column(ForeignKey("simulados.id"), nullable=False)
    questao_id: Mapped[int] = mapped_column(ForeignKey("questoes.id"), nullable=False)
    alternativa_id: Mapped[int] = mapped_column(
        ForeignKey("alternativas.id"), nullable=False
    )
    correta: Mapped[bool] = mapped_column(Boolean, nullable=False)
    respondida_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    aluno: Mapped["Aluno"] = relationship(back_populates="respostas")
    simulado: Mapped["Simulado"] = relationship(back_populates="respostas")
    questao: Mapped["Questao"] = relationship()
    alternativa: Mapped["Alternativa"] = relationship()

    def __repr__(self) -> str:
        return (
            f"Resposta(aluno_id={self.aluno_id}, simulado_id={self.simulado_id}, "
            f"questao_id={self.questao_id}, correta={self.correta})"
        )
