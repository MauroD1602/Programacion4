from models.libro import LibroBase
from schemas.autor import AutorRespuesta


class LibroRespuesta(LibroBase):
    id: int
    autores: list[AutorRespuesta] = []
