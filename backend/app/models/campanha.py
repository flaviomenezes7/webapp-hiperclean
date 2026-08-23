import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Text, SmallInteger, Integer, Boolean, DateTime, func

from app.models.enums import TipoGatilho

if TYPE_CHECKING:
    from app.models.envio import Envio


class RegraCampanha(SQLModel, table=True):
    """Regra de campanha configurável para gerar mensagens automáticas."""
    __tablename__ = "regras_campanha"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    nome: str = Field(sa_column=Column(String(200), nullable=False))
    emoji: Optional[str] = Field(
        default=None,
        sa_column=Column(String(10), nullable=True),
    )
    tipo_gatilho: TipoGatilho = Field(
        sa_column=Column(
            String(30),
            nullable=False,
            index=True,
        )
    )
    dias_offset: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    mes_fixo: Optional[int] = Field(
        default=None,
        sa_column=Column(SmallInteger, nullable=True),
    )
    dia_fixo: Optional[int] = Field(
        default=None,
        sa_column=Column(SmallInteger, nullable=True),
    )
    template_msg: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    ativa: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default="true", index=True),
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
    envios: list["Envio"] = Relationship(back_populates="campanha")
