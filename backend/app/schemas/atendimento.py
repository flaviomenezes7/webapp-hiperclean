import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from app.models.enums import TipoServico


class AtendimentoCreate(BaseModel):
    cliente_id: uuid.UUID
    tipo_servico: TipoServico
    data_atend: date
    observacoes: Optional[str] = None
    valor: Optional[Decimal] = None


class AtendimentoUpdate(BaseModel):
    tipo_servico: Optional[TipoServico] = None
    data_atend: Optional[date] = None
    observacoes: Optional[str] = None
    valor: Optional[Decimal] = None


class AtendimentoRead(BaseModel):
    id: uuid.UUID
    cliente_id: uuid.UUID
    tipo_servico: TipoServico
    data_atend: date
    observacoes: Optional[str] = None
    valor: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    # Include client name for display purposes
    cliente_nome: Optional[str] = None

    model_config = {"from_attributes": True}
