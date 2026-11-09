from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.prestamo import Prestamo

class Socio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)
    activo: bool = Field(default=True)

    prestamos: List["Prestamo"] = Relationship(back_populates="socio")