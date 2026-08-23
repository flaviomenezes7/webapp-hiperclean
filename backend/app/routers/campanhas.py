import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_db
from app.auth import get_current_user
from app.models.campanha import RegraCampanha
from app.schemas.campanha import CampanhaCreate, CampanhaUpdate, CampanhaRead

router = APIRouter(prefix="/campanhas", tags=["Campanhas"])


@router.get("", response_model=list[CampanhaRead])
def list_campanhas(
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Lista todas as regras de campanha."""
    campanhas = session.exec(select(RegraCampanha)).all()
    return [CampanhaRead.model_validate(c) for c in campanhas]


@router.post("", response_model=CampanhaRead, status_code=status.HTTP_201_CREATED)
def create_campanha(
    data: CampanhaCreate,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Cria uma nova regra de campanha."""
    campanha = RegraCampanha(**data.model_dump())
    session.add(campanha)
    session.commit()
    session.refresh(campanha)
    return CampanhaRead.model_validate(campanha)


@router.get("/{campanha_id}", response_model=CampanhaRead)
def get_campanha(
    campanha_id: uuid.UUID,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Retorna uma campanha pelo ID."""
    campanha = session.get(RegraCampanha, campanha_id)
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return CampanhaRead.model_validate(campanha)


@router.put("/{campanha_id}", response_model=CampanhaRead)
def update_campanha(
    campanha_id: uuid.UUID,
    data: CampanhaUpdate,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Atualiza uma campanha existente."""
    campanha = session.get(RegraCampanha, campanha_id)
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campanha, key, value)

    session.add(campanha)
    session.commit()
    session.refresh(campanha)
    return CampanhaRead.model_validate(campanha)


@router.delete("/{campanha_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campanha(
    campanha_id: uuid.UUID,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Remove uma campanha."""
    campanha = session.get(RegraCampanha, campanha_id)
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")

    session.delete(campanha)
    session.commit()


@router.patch("/{campanha_id}/toggle", response_model=CampanhaRead)
def toggle_campanha(
    campanha_id: uuid.UUID,
    session: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Ativa ou desativa uma campanha."""
    campanha = session.get(RegraCampanha, campanha_id)
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")

    campanha.ativa = not campanha.ativa
    session.add(campanha)
    session.commit()
    session.refresh(campanha)
    return CampanhaRead.model_validate(campanha)
