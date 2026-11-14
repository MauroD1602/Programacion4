from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

if TYPE_CHECKING:
    from models.prestamo import Prestamo
    from models.usuario import Usuario


class SocioBase(SQLModel):
    nombre: str
    email: EmailStr = Field(unique=True, index=True)
    activo: bool = Field(default=True)


class Socio(SocioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    prestamos: List["Prestamo"] = Relationship(back_populates="socio")
    # al borrar un socio se borran también sus cuentas de acceso (cascade_delete)
    usuarios: List["Usuario"] = Relationship(back_populates="socio", cascade_delete=True)
