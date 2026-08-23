import uuid
import re
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ClienteCreate(BaseModel):
    nome: str
    telefone: str
    data_nasc: Optional[date] = None
    endereco: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        # Strip everything except digits
        digits = re.sub(r"\D", "", v)
        # Expect Brazilian format: 55 + DDD(2) + number(8-9) = 12 or 13 digits
        if not (12 <= len(digits) <= 13):
            raise ValueError(
                "Telefone deve ter 12 ou 13 dígitos no formato 55DDDNUMERO "
                "(ex: 5511999887766)"
            )
        if not digits.startswith("55"):
            raise ValueError("Telefone deve começar com 55 (código do Brasil)")
        return digits

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        return v


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    data_nasc: Optional[date] = None
    endereco: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = re.sub(r"\D", "", v)
        if not (12 <= len(digits) <= 13):
            raise ValueError(
                "Telefone deve ter 12 ou 13 dígitos no formato 55DDDNUMERO"
            )
        if not digits.startswith("55"):
            raise ValueError("Telefone deve começar com 55 (código do Brasil)")
        return digits


class ClienteRead(BaseModel):
    id: uuid.UUID
    nome: str
    telefone: str
    data_nasc: Optional[date] = None
    endereco: Optional[str] = None
    observacoes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClienteList(BaseModel):
    items: list[ClienteRead]
    total: int
