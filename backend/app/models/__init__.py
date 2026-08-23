# Import all models so Alembic and SQLModel can discover them
from app.models.enums import TipoServico, TipoGatilho
from app.models.cliente import Cliente
from app.models.atendimento import Atendimento
from app.models.campanha import RegraCampanha
from app.models.envio import Envio

__all__ = [
    "TipoServico",
    "TipoGatilho",
    "Cliente",
    "Atendimento",
    "RegraCampanha",
    "Envio",
]
