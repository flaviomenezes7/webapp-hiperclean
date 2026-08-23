import uuid
from datetime import date, datetime
from pydantic import BaseModel


class EnvioCreate(BaseModel):
    cliente_id: uuid.UUID
    campanha_id: uuid.UUID
    referencia_data: date


class EnvioRead(BaseModel):
    id: uuid.UUID
    cliente_id: uuid.UUID
    campanha_id: uuid.UUID
    referencia_data: date
    enviado_em: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
