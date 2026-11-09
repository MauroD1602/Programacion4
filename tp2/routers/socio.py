from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from database import get_session

from models.socio import Socio
from services import prestamo as prestamo_service

router = APIRouter(prefix="/socios", tags=["Socios"])

@router.post("/", response_model=Socio, status_code=status.HTTP_201_CREATED)
def create_Socio(socio: Socio, session: Session = Depends(get_session)):

    socio_existente = session.exec(select(Socio).where(Socio.email == socio.email)).first()
    if socio_existente:
        raise HTTPException(status_code=409, detail="El email ya está registrado.")
    
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio

@router.get("/", response_model=list[Socio])
def get_socios(session: Session = Depends(get_session)):
    socios = session.exec(select(Socio)).all()
    return socios

@router.get("/{socio_id}", response_model=Socio)
def get_socio(socio_id: int, session: Session = Depends(get_session)):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return socio

@router.put("/{socio_id}", response_model=Socio)
def update_socio(socio_id: int, socio_data: Socio, session: Session = Depends(get_session)):
    socio_db = session.get(Socio, socio_id)
    if not socio_db:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    
    if socio_db.email != socio_data.email:
        email_existente = session.exec(select(Socio).where(Socio.email == socio_data.email)).first()
        if email_existente:
            raise HTTPException(status_code=409, detail="El email ya está registrado.")

    socio_db.nombre = socio_data.nombre
    socio_db.email = socio_data.email
    socio_db.activo = socio_data.activo

    session.add(socio_db)
    session.commit()
    session.refresh(socio_db)
    return socio_db

@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_socio(socio_id: int, session: Session = Depends(get_session)):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    
    session.delete(socio)
    session.commit()
    return

@router.get("/{socio_id}/prestamos")
def get_prestamos_del_socio(socio_id: int, activos: Optional[bool] = None, session: Session = Depends(get_session)):
    return prestamo_service.listar_prestamos(session, socio_id, activos)