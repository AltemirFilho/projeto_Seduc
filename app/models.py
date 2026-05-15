from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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
