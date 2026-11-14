from collections.abc import Sequence
from typing import Optional

from sqlmodel import select

from models.socio import Socio, SocioBase
from repositories.database import SessionDep


class SocioRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def fetch_socios(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        return self.session.exec(select(Socio).offset(offset).limit(limit)).all()

    def get_by_id(self, socio_id: int) -> Optional[Socio]:
        return self.session.get(Socio, socio_id)

    def get_by_email(self, email: str) -> Optional[Socio]:
        return self.session.exec(select(Socio).where(Socio.email == email)).first()

    def create_socio(self, datos: SocioBase) -> Socio:
        socio = Socio(**datos.model_dump())
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def update_socio(self, socio: Socio, datos: SocioBase) -> Socio:
        socio.sqlmodel_update(datos.model_dump())
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def delete_socio(self, socio: Socio) -> None:
        # por el cascade_delete del modelo, también se borran sus cuentas de acceso
        self.session.delete(socio)
        self.session.commit()
