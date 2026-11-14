from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException

from models.autor import Autor, AutorBase
from repositories.autor import AutorRepository


class AutorService:
    def __init__(self, repo: Annotated[AutorRepository, Depends()]):
        self.repo = repo

    def get_autores(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        return self.repo.fetch_autores(offset, limit)

    def get_autor(self, autor_id: int) -> Autor:
        autor = self.repo.get_by_id(autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado.")  # Regla 7
        return autor

    def create_autor(self, datos: AutorBase) -> Autor:
        return self.repo.create_autor(datos)

    def update_autor(self, autor_id: int, datos: AutorBase) -> Autor:
        autor = self.get_autor(autor_id)
        return self.repo.update_autor(autor, datos)

    def delete_autor(self, autor_id: int) -> None:
        autor = self.get_autor(autor_id)
        self.repo.delete_autor(autor)
