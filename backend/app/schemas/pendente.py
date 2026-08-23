import uuid
from datetime import date
from typing import Optional
from pydantic import BaseModel

from app.models.enums import TipoGatilho


class PendenteItem(BaseModel):
    """Um item pendente: um cliente que precisa ser contactado hoje."""
    cliente_id: uuid.UUID
    cliente_nome: str
    cliente_telefone: str
    cliente_iniciais: str
    campanha_id: uuid.UUID
    referencia_data: date
    mensagem_formatada: str
    link_whatsapp: str


class CampanhaGroup(BaseModel):
    """Grupo de pendentes agrupados por campanha."""
    campanha_id: uuid.UUID
    campanha_nome: str
    campanha_emoji: Optional[str] = None
    tipo_gatilho: TipoGatilho
    pendentes: list[PendenteItem]
    total: int


class PendentesHojeResponse(BaseModel):
    """Resposta do endpoint /pendentes/hoje."""
    data: date
    grupos: list[CampanhaGroup]
    total_pendentes: int
    total_enviados_hoje: int
