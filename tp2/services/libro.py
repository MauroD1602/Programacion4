from collections.abc import Sequence
from typing import Annotated, Optional

from fastapi import Depends, HTTPException

from models.libro import Libro, LibroBase
from repositories.autor import AutorRepository
from repositories.libro import LibroRepository


class LibroService:
    def __init__(
        self,
        repo: Annotated[LibroRepository, Depends()],
        autor_repo: Annotated[AutorRepository, Depends()],
    ):
        self.repo = repo
        self.autor_repo = autor_repo

    def get_libros(self, disponibles: Optional[bool] = None, offset: int = 0, limit: int = 100) -> Sequence[Libro]:
        return self.repo.fetch_libros(disponibles, offset, limit)

    def get_libro(self, libro_id: int) -> Libro:
        libro = self.repo.get_by_id(libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado.")  # Regla 7
        return libro

    def create_libro(self, datos: LibroBase) -> Libro:
        if self.repo.get_by_isbn(datos.isbn):
            raise HTTPException(status_code=409, detail="El ISBN ya está registrado.")  # Regla 8
        return self.repo.create_libro(datos)

    def update_libro(self, libro_id: int, datos: LibroBase) -> Libro:
        libro = self.get_libro(libro_id)
        if libro.isbn != datos.isbn and self.repo.get_by_isbn(datos.isbn):
            raise HTTPException(status_code=409, detail="El ISBN ya está registrado.")  # Regla 8
        return self.repo.update_libro(libro, datos)

    def delete_libro(self, libro_id: int) -> None:
        libro = self.get_libro(libro_id)
        if libro.prestamos:
            raise HTTPException(status_code=409, detail="No se puede borrar un libro con préstamos.")
        self.repo.delete_libro(libro)

    def asociar_autor(self, libro_id: int, autor_id: int) -> Libro:
        libro = self.get_libro(libro_id)
        autor = self.autor_repo.get_by_id(autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado.")  # Regla 7
        if autor in libro.autores:
            raise HTTPException(status_code=409, detail="El autor ya está asociado al libro.")
        return self.repo.add_autor(libro, autor)
