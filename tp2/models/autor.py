from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from models.libro_autor import LibroAutor

if TYPE_CHECKING:
    from models.libro import Libro

class Autor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: str

    libro: List["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)