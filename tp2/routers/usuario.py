from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from dependencies import UsuarioServiceDep, permission_check
from middlewares.protected import protected
from schemas.usuario import UsuarioCrear, UsuarioRespuesta

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(HTTPBearer()), Depends(permission_check("administrar_usuarios"))],
)


@router.post("", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
@protected
def create_usuario(datos: UsuarioCrear, service: UsuarioServiceDep):
    return service.create_usuario(datos)
