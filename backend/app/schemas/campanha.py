import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator

from app.models.enums import TipoGatilho


class CampanhaCreate(BaseModel):
    nome: str
    emoji: Optional[str] = None
    tipo_gatilho: TipoGatilho
    dias_offset: Optional[int] = None
    mes_fixo: Optional[int] = None
    dia_fixo: Optional[int] = None
    template_msg: str
    ativa: bool = True

    @model_validator(mode="after")
    def validate_trigger_fields(self):
        if self.tipo_gatilho == TipoGatilho.DIAS_APOS_ATENDIMENTO:
            if self.dias_offset is None or self.dias_offset <= 0:
                raise ValueError(
                    "dias_offset é obrigatório e deve ser > 0 para gatilho DIAS_APOS_ATENDIMENTO"
                )
        elif self.tipo_gatilho == TipoGatilho.DATA_FIXA:
            if self.mes_fixo is None or self.dia_fixo is None:
                raise ValueError(
                    "mes_fixo e dia_fixo são obrigatórios para gatilho DATA_FIXA"
                )
            if not (1 <= self.mes_fixo <= 12):
                raise ValueError("mes_fixo deve estar entre 1 e 12")
            if not (1 <= self.dia_fixo <= 31):
                raise ValueError("dia_fixo deve estar entre 1 e 31")
        # ANIVERSARIO doesn't need extra fields
        return self


class CampanhaUpdate(BaseModel):
    nome: Optional[str] = None
    emoji: Optional[str] = None
    tipo_gatilho: Optional[TipoGatilho] = None
    dias_offset: Optional[int] = None
    mes_fixo: Optional[int] = None
    dia_fixo: Optional[int] = None
    template_msg: Optional[str] = None
    ativa: Optional[bool] = None


class CampanhaRead(BaseModel):
    id: uuid.UUID
    nome: str
    emoji: Optional[str] = None
    tipo_gatilho: TipoGatilho
    dias_offset: Optional[int] = None
    mes_fixo: Optional[int] = None
    dia_fixo: Optional[int] = None
    template_msg: str
    ativa: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
