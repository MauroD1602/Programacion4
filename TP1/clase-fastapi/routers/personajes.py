from fastapi import APIRouter, HTTPException, status
from typing import Optional
from models.personajes import (
    Personaje,
    GetPersonajesResponse,
    CreatePersonajeResponse,
    UpdatePersonajeResponse,
    DeletePersonajeResponse
)

router = APIRouter()

personajes_db: list[Personaje] = [
    Personaje(id=1, nombre="Gimli", raza="Enano", clase="Guerrero", nivel=3)
]

@router.get("/personaje")
def get_personajes(clase: Optional[str] = None) -> GetPersonajesResponse:
    if clase:
        filtrados = [p for p in personajes_db if p.clase.lower() == clase.lower()]
        return GetPersonajesResponse(personajes=filtrados)
    return GetPersonajesResponse(personajes=personajes_db)

@router.get("/personaje/{id}")
def get_personaje_by_id(id: int) -> Personaje:
    for p in personajes_db:
        if p.id == id:
            return p
    raise HTTPException(status_code=404, detail="Personaje no encontrado")

@router.post("/personaje")
def create_personaje(personaje: Personaje) -> CreatePersonajeResponse:
    personajes_db.append(personaje)
    return CreatePersonajeResponse(message="Personaje creado exitosamente")

@router.put("/personaje/{id}")
def update_personaje(id: int, personaje_data: Personaje) -> UpdatePersonajeResponse:
    for index, p in enumerate(personajes_db):
        if p.id == id:
            personaje_data.id = id
            personajes_db[index] = personaje_data
            return UpdatePersonajeResponse(message="Personaje actualizado", personaje=personaje_data)
    raise HTTPException(status_code=404, detail="Personaje no encontrado")

@router.delete("/personaje/{id}")
def delete_personaje(id: int) -> DeletePersonajeResponse:
    for p in personajes_db:
        if p.id == id:
            personajes_db.remove(p)
            return DeletePersonajeResponse(message="Personaje eliminado")
    raise HTTPException(status_code=404, detail="Personaje no encontrado")