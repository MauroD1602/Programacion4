from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from models.libro_autor import LibroAutor

if TYPE_CHECKING:
    from models.libro import Libro


class AutorBase(SQLModel):
    nombre: str
    nacionalidad: str


class Autor(AutorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    libros: List["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)
