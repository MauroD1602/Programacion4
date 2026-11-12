from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from models.libro_autor import LibroAutor

if TYPE_CHECKING:
    from models.autor import Autor
    from models.prestamo import Prestamo

class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    isbn: str = Field(unique=True, index=True)
    stock: int = Field(default=0, ge=0)
    anio: int

    autores: List["Autor"] = Relationship(back_populates="libros", link_model=LibroAutor)   
    prestamos: List["Prestamo"] = Relationship(back_populates="libro")