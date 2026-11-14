from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from pydantic import EmailStr

from models.roles import Rol, UsuarioRol

if TYPE_CHECKING:
    from models.socio import Socio


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    password: str  # hash bcrypt: nunca se guarda la contraseña en texto plano
    socio_id: Optional[int] = Field(default=None, foreign_key="socio.id")

    socio: Optional["Socio"] = Relationship(back_populates="usuarios")
    roles: List[Rol] = Relationship(back_populates="usuarios", link_model=UsuarioRol)
