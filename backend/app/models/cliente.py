import uuid
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Text, Date, DateTime, func

if TYPE_CHECKING:
    from app.models.atendimento import Atendimento
    from app.models.envio import Envio


class Cliente(SQLModel, table=True):
    """Cliente da Hiper Clean."""
    __tablename__ = "clientes"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    nome: str = Field(sa_column=Column(String(200), nullable=False))
    telefone: str = Field(sa_column=Column(String(20), nullable=False, index=True))
    data_nasc: Optional[date] = Field(
        default=None,
        sa_column=Column(Date, nullable=True, index=True),
    )
    endereco: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    observacoes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    # Relationships
    atendimentos: list["Atendimento"] = Relationship(back_populates="cliente")
    envios: list["Envio"] = Relationship(back_populates="cliente")
