from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer

from dependencies import AutorServiceDep, permission_check
from middlewares.protected import protected
from models.autor import AutorBase
from schemas.autor import AutorRespuesta

router = APIRouter(prefix="/autores", tags=["Autores"], dependencies=[Depends(HTTPBearer())])

puede_leer = Depends(permission_check("leer_catalogo"))
puede_escribir = Depends(permission_check("escribir_catalogo"))


@router.post("", response_model=AutorRespuesta, status_code=status.HTTP_201_CREATED, dependencies=[puede_escribir])
@protected
def create_autor(datos: AutorBase, service: AutorServiceDep):
    return service.create_autor(datos)


@router.get("", response_model=list[AutorRespuesta], dependencies=[puede_leer])
@protected
def get_autores(
    service: AutorServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return service.get_autores(offset, limit)


@router.get("/{autor_id}", response_model=AutorRespuesta, dependencies=[puede_leer])
@protected
def get_autor(autor_id: int, service: AutorServiceDep):
    return service.get_autor(autor_id)


@router.put("/{autor_id}", response_model=AutorRespuesta, dependencies=[puede_escribir])
@protected
def update_autor(autor_id: int, datos: AutorBase, service: AutorServiceDep):
    return service.update_autor(autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[puede_escribir])
@protected
def delete_autor(autor_id: int, service: AutorServiceDep):
    service.delete_autor(autor_id)
