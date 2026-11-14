from datetime import date
from typing import Optional

from sqlmodel import SQLModel


class PrestamoCrear(SQLModel):
    socio_id: int
    libro_id: int


class PrestamoRespuesta(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: Optional[date] = None
    multa: float
