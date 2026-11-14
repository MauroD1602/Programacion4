import os
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from models.usuario import Usuario
from repositories.usuario import UsuarioRepository
from services.autor import AutorService
from services.jwt_service import JWTService
from services.libro import LibroService
from services.login import LoginService
from services.prestamo import PrestamoService
from services.socio import SocioService
from services.usuario import UsuarioService

# Alias para pedir cada pieza como dependencia, por ejemplo: `def endpoint(service: LibroServiceDep)`
UsuarioRepositoryDep = Annotated[UsuarioRepository, Depends()]

AutorServiceDep = Annotated[AutorService, Depends()]
LibroServiceDep = Annotated[LibroService, Depends()]
SocioServiceDep = Annotated[SocioService, Depends()]
PrestamoServiceDep = Annotated[PrestamoService, Depends()]
UsuarioServiceDep = Annotated[UsuarioService, Depends()]
LoginServiceDep = Annotated[LoginService, Depends()]


# ---------------- JWT ----------------
# Solo para desarrollo: en un entorno real se define la variable JWT_SECRET_KEY
CLAVE_POR_DEFECTO = "clave-solo-para-desarrollo-no-usar-en-produccion"


def get_jwt_service() -> JWTService:
    return JWTService(os.getenv("JWT_SECRET_KEY", CLAVE_POR_DEFECTO))


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]


# ---------------- Usuario logueado y permisos ----------------
def get_current_user(request: Request, repo: UsuarioRepositoryDep) -> Usuario:
    # El token ya lo validó JWTAuthMW, que dejó el contenido en request.state
    payload = getattr(request.state, "jwt_payload", None)
    if payload is None:
        raise HTTPException(status_code=401, detail="Falta el token: iniciá sesión en /login.")

    usuario = repo.get_by_email(payload.get("sub"))
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado.")

    return usuario


CurrentUserDep = Annotated[Usuario, Depends(get_current_user)]


def tiene_permiso(usuario: Usuario, nombre: str) -> bool:
    return any(permiso.nombre == nombre for rol in usuario.roles for permiso in rol.permisos)


def permission_check(nombre: str):
    """Devuelve una dependencia que responde 403 si el usuario logueado no tiene ese permiso."""

    def check(me: CurrentUserDep) -> None:
        if not tiene_permiso(me, nombre):
            raise HTTPException(status_code=403, detail=f"Falta el permiso: {nombre}")

    return check
