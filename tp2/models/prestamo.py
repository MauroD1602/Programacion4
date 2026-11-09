from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

if TYPE_CHECKING:
    from models.socio import Socio
    from models.libro import Libro

class Prestamo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: int = Field(foreign_key="socio.id")
    libro_id: int = Field(foreign_key="libro.id")
    fecha_prestamo: str
    fecha_venciiemiento: str
    fecha_devolucion: Optional[date] = Field(default=None)
    multa: Optional[float] = None

    socio: "Socio" = Relationship(back_populates="prestamos")
    libro: "Libro" = Relationship(back_populates="prestamos")