from collections.abc import Sequence
from typing import Optional

from sqlmodel import select, col

from models.libro import Libro
from models.prestamo import Prestamo
from repositories.database import SessionDep


class PrestamoRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_id(self, prestamo_id: int) -> Optional[Prestamo]:
        return self.session.get(Prestamo, prestamo_id)

    def fetch_by_socio(self, socio_id: int, activos: Optional[bool] = None) -> Sequence[Prestamo]:
        query = select(Prestamo).where(Prestamo.socio_id == socio_id)
        if activos is not None:
            if activos:
                query = query.where(col(Prestamo.fecha_devolucion).is_(None))
            else:
                query = query.where(col(Prestamo.fecha_devolucion).is_not(None))
        return self.session.exec(query).all()

    def guardar(self, prestamo: Prestamo, libro: Libro) -> Prestamo:
        # el préstamo y el stock del libro se guardan juntos, en una sola transacción
        self.session.add(prestamo)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(prestamo)
        return prestamo
