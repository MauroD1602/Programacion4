from fastapi import APIRouter, Depends, Body, status
from sqlmodel import Session
from database import get_session

from services import prestamo as prestamo_service

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_prestamo(
    socio_id: int = Body(),
    libro_id: int = Body(),
    session: Session = Depends(get_session)
):
    return prestamo_service.crear_prestamo(session, socio_id, libro_id)

@router.post("/{prestamo_id}/devolucion")
def devolver_prestamo(
    prestamo_id: int,
    session: Session = Depends(get_session)
):
    return prestamo_service.devolver_prestamo(session, prestamo_id)