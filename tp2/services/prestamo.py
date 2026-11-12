from datetime import date, timedelta
from typing import List, Optional
from fastapi import HTTPException
from sqlmodel import Session, select, col

from models.libro import Libro
from models.socio import Socio
from models.prestamo import Prestamo

MAX_PRESTAMOS_ACTIVOS = 3
DIAS_PRESTAMO = 14
MULTA_POR_DIA = 100

def crear_prestamo(session: Session, socio_id: int, libro_id: int):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")

    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    if not socio.activo:
        raise HTTPException(status_code=403, detail="El socio no está activo.")

    prestamos_activos = session.exec(
        select(Prestamo).where(
            Prestamo.socio_id == socio_id,
            Prestamo.fecha_devolucion == None
        )
    ).all()

    if len(prestamos_activos) >= MAX_PRESTAMOS_ACTIVOS:
        raise HTTPException(status_code=409, detail="Limite alcanzado (Maximo 3 activos).")

    if libro.stock <= 0:
        raise HTTPException(status_code=409, detail="No hay stock del libro.")

    hoy = date.today()
    prestamo = Prestamo(
        socio_id=socio_id,
        libro_id=libro_id,
        fecha_prestamo=hoy,
        fecha_vencimiento=hoy + timedelta(days=DIAS_PRESTAMO),
    )
    libro.stock -= 1

    session.add(prestamo)
    session.add(libro)
    session.commit()
    session.refresh(prestamo)
    return prestamo

def devolver_prestamo(session: Session, prestamo_id: int):
    prestamo = session.get(Prestamo, prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado.")

    if prestamo.fecha_devolucion is not None:
        raise HTTPException(status_code=409, detail="El prestamo ya fue devuelto.")

    hoy = date.today()
    dias_atraso = (hoy - prestamo.fecha_vencimiento).days
    if dias_atraso < 0:
        dias_atraso = 0

    prestamo.fecha_devolucion = hoy
    prestamo.multa = MULTA_POR_DIA * dias_atraso

    prestamo.libro.stock += 1

    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo

def listar_prestamos(session: Session, socio_id: int, activos: Optional[bool]):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")

    query = select(Prestamo).where(Prestamo.socio_id == socio_id)

    if activos is not None:
        if activos:
            query = query.where(col(Prestamo.fecha_devolucion).is_(None))
        else:
            query = query.where(col(Prestamo.fecha_devolucion).is_not(None))

    return session.exec(query).all()