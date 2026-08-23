from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.pendente import PendentesHojeResponse
from app.services.pendentes import get_pendentes_hoje

router = APIRouter(prefix="/pendentes", tags=["Pendentes"])


@router.get("/hoje", response_model=PendentesHojeResponse)
def pendentes_hoje(
    data: Optional[date] = Query(
        None,
        description="Data para consulta (padrão: hoje). Útil para testes.",
    ),
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """
    Retorna a lista de pendentes de hoje (ou da data informada),
    agrupados por campanha, com mensagem formatada e link WhatsApp.
    """
    return get_pendentes_hoje(session, hoje=data)
