from typing import Optional, Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer

from dependencies import LibroServiceDep, permission_check
from middlewares.protected import protected
from models.libro import LibroBase
from schemas.libro import LibroRespuesta

router = APIRouter(prefix="/libros", tags=["Libros"], dependencies=[Depends(HTTPBearer())])

puede_leer = Depends(permission_check("leer_catalogo"))
puede_escribir = Depends(permission_check("escribir_catalogo"))


@router.post("", response_model=LibroRespuesta, status_code=status.HTTP_201_CREATED, dependencies=[puede_escribir])
@protected
def create_libro(datos: LibroBase, service: LibroServiceDep):
    return service.create_libro(datos)


@router.get("", response_model=list[LibroRespuesta], dependencies=[puede_leer])
@protected
def get_libros(
    service: LibroServiceDep,
    disponibles: Optional[bool] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return service.get_libros(disponibles, offset, limit)


@router.get("/{libro_id}", response_model=LibroRespuesta, dependencies=[puede_leer])
@protected
def get_libro(libro_id: int, service: LibroServiceDep):
    return service.get_libro(libro_id)


@router.put("/{libro_id}", response_model=LibroRespuesta, dependencies=[puede_escribir])
@protected
def update_libro(libro_id: int, datos: LibroBase, service: LibroServiceDep):
    return service.update_libro(libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[puede_escribir])
@protected
def delete_libro(libro_id: int, service: LibroServiceDep):
    service.delete_libro(libro_id)


@router.post("/{libro_id}/autores/{autor_id}", response_model=LibroRespuesta, dependencies=[puede_escribir])
@protected
def asociar_autor_con_libro(libro_id: int, autor_id: int, service: LibroServiceDep):
    return service.asociar_autor(libro_id, autor_id)
