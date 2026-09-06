import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlmodel import Session, select, col, func

from app.database import get_db
from app.auth import get_current_user
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteRead, ClienteList

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/importar-excel", tags=["Importação"])
def importar_excel(
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """
    Importa clientes e atendimentos de uma planilha Excel (.xlsx).
    Deduplica pelo telefone — clientes já existentes no banco são pulados.
    """
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Arquivo inválido. Envie um arquivo .xlsx",
        )

    from app.services.importacao import importar_excel as do_import

    try:
        file_bytes = file.file.read()
        result = do_import(session, file_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar planilha: {str(e)}")


@router.get("", response_model=ClienteList)
def list_clientes(
    busca: Optional[str] = Query(None, description="Buscar por nome"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Lista clientes ativos com paginação e busca por nome."""
    stmt = select(Cliente).where(Cliente.deleted_at.is_(None))  # type: ignore

    if busca:
        stmt = stmt.where(col(Cliente.nome).ilike(f"%{busca}%"))

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.exec(count_stmt).one()

    # Paginate
    stmt = stmt.order_by(col(Cliente.nome)).offset(skip).limit(limit)
    clientes = session.exec(stmt).all()

    return ClienteList(
        items=[ClienteRead.model_validate(c) for c in clientes],
        total=total,
    )


@router.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def create_cliente(
    data: ClienteCreate,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Cria um novo cliente."""
    cliente = Cliente(**data.model_dump())
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return ClienteRead.model_validate(cliente)


@router.get("/{cliente_id}", response_model=ClienteRead)
def get_cliente(
    cliente_id: uuid.UUID,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Retorna um cliente pelo ID."""
    cliente = session.get(Cliente, cliente_id)
    if not cliente or cliente.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return ClienteRead.model_validate(cliente)


@router.put("/{cliente_id}", response_model=ClienteRead)
def update_cliente(
    cliente_id: uuid.UUID,
    data: ClienteUpdate,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Atualiza um cliente existente."""
    cliente = session.get(Cliente, cliente_id)
    if not cliente or cliente.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)

    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return ClienteRead.model_validate(cliente)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(
    cliente_id: uuid.UUID,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Soft delete de um cliente."""
    cliente = session.get(Cliente, cliente_id)
    if not cliente or cliente.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    from datetime import datetime, timezone
    cliente.deleted_at = datetime.now(timezone.utc)
    session.add(cliente)
    session.commit()
