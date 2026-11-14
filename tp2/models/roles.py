from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.usuario import Usuario

ROL_BIBLIOTECARIO = "bibliotecario"
ROL_SOCIO = "socio"


# Tablas intermedias (muchos a muchos)
class RolPermiso(SQLModel, table=True):
    rol_id: Optional[int] = Field(default=None, foreign_key="rol.id", primary_key=True)
    permiso_id: Optional[int] = Field(default=None, foreign_key="permiso.id", primary_key=True)


class UsuarioRol(SQLModel, table=True):
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", primary_key=True)
    rol_id: Optional[int] = Field(default=None, foreign_key="rol.id", primary_key=True)


class PermisoBase(SQLModel):
    nombre: str = Field(unique=True, index=True)


class Permiso(PermisoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    roles: List["Rol"] = Relationship(back_populates="permisos", link_model=RolPermiso)


class RolBase(SQLModel):
    nombre: str = Field(unique=True, index=True)


class Rol(RolBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    permisos: List[Permiso] = Relationship(back_populates="roles", link_model=RolPermiso)
    usuarios: List["Usuario"] = Relationship(back_populates="roles", link_model=UsuarioRol)
