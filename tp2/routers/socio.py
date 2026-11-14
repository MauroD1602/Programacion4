from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from dependencies import CurrentUserDep, PrestamoServiceDep, SocioServiceDep, permission_check, tiene_permiso
from middlewares.protected import protected
from models.socio import SocioBase
from schemas.prestamo import PrestamoRespuesta
from schemas.socio import SocioRespuesta

router = APIRouter(prefix="/socios", tags=["Socios"], dependencies=[Depends(HTTPBearer())])

puede_administrar = Depends(permission_check("administrar_socios"))


@router.post("", response_model=SocioRespuesta, status_code=status.HTTP_201_CREATED, dependencies=[puede_administrar])
@protected
def create_socio(datos: SocioBase, service: SocioServiceDep):
    return service.create_socio(datos)


@router.get("", response_model=list[SocioRespuesta], dependencies=[puede_administrar])
@protected
def get_socios(
    service: SocioServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return service.get_socios(offset, limit)


@router.get("/{socio_id}", response_model=SocioRespuesta, dependencies=[puede_administrar])
@protected
def get_socio(socio_id: int, service: SocioServiceDep):
    return service.get_socio(socio_id)


@router.put("/{socio_id}", response_model=SocioRespuesta, dependencies=[puede_administrar])
@protected
def update_socio(socio_id: int, datos: SocioBase, service: SocioServiceDep):
    return service.update_socio(socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[puede_administrar])
@protected
def delete_socio(socio_id: int, service: SocioServiceDep):
    service.delete_socio(socio_id)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRespuesta])
@protected
def get_prestamos_del_socio(
    socio_id: int,
    me: CurrentUserDep,
    service: PrestamoServiceDep,
    activos: Optional[bool] = None,
):
    # El bibliotecario ve los préstamos de cualquiera; un socio, solo los suyos
    if not tiene_permiso(me, "ver_todos_los_prestamos"):
        es_el_propio = tiene_permiso(me, "ver_prestamos_propios") and me.socio_id == socio_id
        if not es_el_propio:
            raise HTTPException(status_code=403, detail="Solo podés ver tus propios préstamos.")

    return service.listar_prestamos(socio_id, activos)
