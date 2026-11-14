from typing import Annotated

from fastapi import Depends, HTTPException

from models.roles import ROL_SOCIO
from models.usuario import Usuario
from repositories.rol import RolRepository
from repositories.socio import SocioRepository
from repositories.usuario import UsuarioRepository
from schemas.usuario import UsuarioCrear
from utils.hash import hash_password


class UsuarioService:
    def __init__(
        self,
        repo: Annotated[UsuarioRepository, Depends()],
        rol_repo: Annotated[RolRepository, Depends()],
        socio_repo: Annotated[SocioRepository, Depends()],
    ):
        self.repo = repo
        self.rol_repo = rol_repo
        self.socio_repo = socio_repo

    def create_usuario(self, datos: UsuarioCrear) -> Usuario:
        if self.repo.get_by_email(datos.email):
            raise HTTPException(status_code=409, detail="El email ya está registrado.")  # Regla 8

        socio_id = None
        if datos.rol == ROL_SOCIO:
            if datos.socio_id is None:
                raise HTTPException(status_code=422, detail="Un usuario con rol socio necesita socio_id.")
            if not self.socio_repo.get_by_id(datos.socio_id):
                raise HTTPException(status_code=404, detail="Socio no encontrado.")  # Regla 7
            socio_id = datos.socio_id

        rol = self.rol_repo.get_by_nombre(datos.rol)
        if not rol:
            raise HTTPException(status_code=422, detail="El rol no existe.")

        return self.repo.create_usuario(datos.email, hash_password(datos.password), rol, socio_id)
