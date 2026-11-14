from collections.abc import Sequence
from typing import Optional

from sqlmodel import select

from models.autor import Autor, AutorBase
from repositories.database import SessionDep


class AutorRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def fetch_autores(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        return self.session.exec(select(Autor).offset(offset).limit(limit)).all()

    def get_by_id(self, autor_id: int) -> Optional[Autor]:
        return self.session.get(Autor, autor_id)

    def create_autor(self, datos: AutorBase) -> Autor:
        autor = Autor(**datos.model_dump())
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def update_autor(self, autor: Autor, datos: AutorBase) -> Autor:
        autor.sqlmodel_update(datos.model_dump())
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def delete_autor(self, autor: Autor) -> None:
        self.session.delete(autor)
        self.session.commit()
