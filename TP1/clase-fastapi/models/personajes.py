from pydantic import BaseModel
from typing import List

class Personaje(BaseModel):
    id: int
    nombre: str
    raza: str
    clase: str
    nivel: int

class GetPersonajesResponse(BaseModel):
    personajes: List[Personaje]

class CreatePersonajeResponse(BaseModel):
    message: str

class UpdatePersonajeResponse(BaseModel):
    message: str
    personaje: Personaje

class DeletePersonajeResponse(BaseModel):
    message: str