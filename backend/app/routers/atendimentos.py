import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, col, func

from app.database import get_db
from app.auth import get_current_user
from app.models.atendimento import Atendimento
from app.models.cliente import Cliente
from app.schemas.atendimento import AtendimentoCreate, AtendimentoUpdate, AtendimentoRead

router = APIRouter(prefix="/atendimentos", tags=["Atendimentos"])


@router.get("")
def list_atendimentos(
    cliente_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Lista atendimentos com filtro opcional por cliente."""
    base_stmt = select(Atendimento)
    if cliente_id:
        base_stmt = base_stmt.where(Atendimento.cliente_id == cliente_id)

    total = session.exec(select(func.count()).select_from(base_stmt.subquery())).one()

    stmt = select(Atendimento, Cliente.nome).join(
        Cliente, Atendimento.cliente_id == Cliente.id
    )
    if cliente_id:
        stmt = stmt.where(Atendimento.cliente_id == cliente_id)

    stmt = stmt.order_by(col(Atendimento.data_atend).desc()).offset(skip).limit(limit)
    results = session.exec(stmt).all()

    items = []
    for atend, cliente_nome in results:
        read = AtendimentoRead.model_validate(atend)
        read.cliente_nome = cliente_nome
        items.append(read)
    return {"items": items, "total": total}


@router.post("", response_model=AtendimentoRead, status_code=status.HTTP_201_CREATED)
def create_atendimento(
    data: AtendimentoCreate,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Registra um novo atendimento."""
    # Verify client exists
    cliente = session.get(Cliente, data.cliente_id)
    if not cliente or cliente.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    atendimento = Atendimento(**data.model_dump())
    session.add(atendimento)
    session.commit()
    session.refresh(atendimento)
    read = AtendimentoRead.model_validate(atendimento)
    read.cliente_nome = cliente.nome
    return read


@router.put("/{atendimento_id}", response_model=AtendimentoRead)
def update_atendimento(
    atendimento_id: uuid.UUID,
    data: AtendimentoUpdate,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Atualiza um atendimento existente."""
    atendimento = session.get(Atendimento, atendimento_id)
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(atendimento, key, value)

    session.add(atendimento)
    session.commit()
    session.refresh(atendimento)
    return AtendimentoRead.model_validate(atendimento)


@router.delete("/{atendimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_atendimento(
    atendimento_id: uuid.UUID,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Remove um atendimento."""
    atendimento = session.get(Atendimento, atendimento_id)
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")

    session.delete(atendimento)
    session.commit()
