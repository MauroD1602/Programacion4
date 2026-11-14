from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from dependencies import PrestamoServiceDep, permission_check
from middlewares.protected import protected
from schemas.prestamo import PrestamoCrear, PrestamoRespuesta

router = APIRouter(
    prefix="/prestamos",
    tags=["Prestamos"],
    dependencies=[Depends(HTTPBearer()), Depends(permission_check("administrar_prestamos"))],
)


@router.post("", response_model=PrestamoRespuesta, status_code=status.HTTP_201_CREATED)
@protected
def crear_prestamo(datos: PrestamoCrear, service: PrestamoServiceDep):
    return service.crear_prestamo(datos.socio_id, datos.libro_id)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoRespuesta)
@protected
def devolver_prestamo(prestamo_id: int, service: PrestamoServiceDep):
    return service.devolver_prestamo(prestamo_id)
