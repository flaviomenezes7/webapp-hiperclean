import uuid
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Date, DateTime, UniqueConstraint, func

if TYPE_CHECKING:
    from app.models.cliente import Cliente
    from app.models.campanha import RegraCampanha


class Envio(SQLModel, table=True):
    """Registro de envio de mensagem realizado (marcado manualmente pelo dono)."""
    __tablename__ = "envios"
    __table_args__ = (
        UniqueConstraint("cliente_id", "campanha_id", "referencia_data", name="uq_envio_cliente_campanha_ref"),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    cliente_id: uuid.UUID = Field(foreign_key="clientes.id", nullable=False, index=True)
    campanha_id: uuid.UUID = Field(foreign_key="regras_campanha.id", nullable=False, index=True)
    referencia_data: date = Field(
        sa_column=Column(Date, nullable=False),
    )
    enviado_em: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )

    # Relationships
    cliente: Optional["Cliente"] = Relationship(back_populates="envios")
    campanha: Optional["RegraCampanha"] = Relationship(back_populates="envios")
