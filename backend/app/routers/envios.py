from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.auth import get_current_user
from app.models.envio import Envio
from app.schemas.envio import EnvioCreate, EnvioRead

router = APIRouter(prefix="/envios", tags=["Envios"])


@router.post("", response_model=EnvioRead, status_code=status.HTTP_201_CREATED)
def registrar_envio(
    data: EnvioCreate,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """
    Registra que uma mensagem foi enviada.
    Chamado pelo frontend quando o dono clica "Enviar" e o WhatsApp abre.
    A unique constraint (cliente_id, campanha_id, referencia_data) previne duplicatas.
    """
    envio = Envio(**data.model_dump())
    session.add(envio)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Envio já registrado para este cliente/campanha/data",
        )
    session.refresh(envio)
    return EnvioRead.model_validate(envio)
