import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Text, Date, DateTime, Numeric, ForeignKey, func

from app.models.enums import TipoServico

if TYPE_CHECKING:
    from app.models.cliente import Cliente


class Atendimento(SQLModel, table=True):
    """Registro de um atendimento/serviço realizado."""
    __tablename__ = "atendimentos"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    cliente_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("clientes.id"),
            nullable=False,
            index=True,
        ),
    )
    tipo_servico: TipoServico = Field(
        sa_column=Column(
            String(30),
            nullable=False,
        )
    )
    data_atend: date = Field(
        sa_column=Column(Date, nullable=False, index=True)
    )
    observacoes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    valor: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
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
    cliente: Optional["Cliente"] = Relationship(back_populates="atendimentos")
