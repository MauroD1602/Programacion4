from typing import Literal, Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class UsuarioCrear(SQLModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=72)
    rol: Literal["bibliotecario", "socio"]
    socio_id: Optional[int] = None


class RolRespuesta(SQLModel):
    id: int
    nombre: str


class UsuarioRespuesta(SQLModel):
    # no incluye la contraseña
    id: int
    email: EmailStr
    socio_id: Optional[int] = None
    roles: list[RolRespuesta] = []
