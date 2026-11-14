from typing import Optional

from sqlmodel import select

from models.roles import Rol
from repositories.database import SessionDep


class RolRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        return self.session.exec(select(Rol).where(Rol.nombre == nombre)).first()
