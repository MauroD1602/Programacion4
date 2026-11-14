from collections.abc import Sequence
from typing import Optional

from sqlmodel import select

from models.autor import Autor
from models.libro import Libro, LibroBase
from repositories.database import SessionDep


class LibroRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def fetch_libros(self, disponibles: Optional[bool] = None, offset: int = 0, limit: int = 100) -> Sequence[Libro]:
        query = select(Libro)
        if disponibles is not None:
            if disponibles:
                query = query.where(Libro.stock > 0)
            else:
                query = query.where(Libro.stock == 0)
        return self.session.exec(query.offset(offset).limit(limit)).all()
    
    def get_by_id(self, libro_id: int) -> Optional[Libro]:
        return self.session.get(Libro, libro_id)

    def get_by_isbn(self, isbn: str) -> Optional[Libro]:
        return self.session.exec(select(Libro).where(Libro.isbn == isbn)).first()

    def create_libro(self, datos: LibroBase) -> Libro:
        libro = Libro(**datos.model_dump())
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def update_libro(self, libro: Libro, datos: LibroBase) -> Libro:
        libro.sqlmodel_update(datos.model_dump())
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def delete_libro(self, libro: Libro) -> None:
        self.session.delete(libro)
        self.session.commit()

    def add_autor(self, libro: Libro, autor: Autor) -> Libro:
        libro.autores.append(autor)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro
