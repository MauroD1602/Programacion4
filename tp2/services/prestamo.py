from collections.abc import Sequence
from datetime import date, timedelta
from typing import Annotated, Optional

from fastapi import Depends, HTTPException

from models.prestamo import Prestamo
from repositories.libro import LibroRepository
from repositories.prestamo import PrestamoRepository
from repositories.socio import SocioRepository

MAX_PRESTAMOS_ACTIVOS = 3
DIAS_PRESTAMO = 14
MULTA_POR_DIA = 100


class PrestamoService:
    def __init__(
        self,
        repo: Annotated[PrestamoRepository, Depends()],
        socio_repo: Annotated[SocioRepository, Depends()],
        libro_repo: Annotated[LibroRepository, Depends()],
    ):
        self.repo = repo
        self.socio_repo = socio_repo
        self.libro_repo = libro_repo

    def crear_prestamo(self, socio_id: int, libro_id: int) -> Prestamo:
        socio = self.socio_repo.get_by_id(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado.")  # Regla 7

        libro = self.libro_repo.get_by_id(libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado.")  # Regla 7

        if not socio.activo:
            raise HTTPException(status_code=403, detail="El socio no está activo.")  # Regla 3

        prestamos_activos = self.repo.fetch_by_socio(socio_id, activos=True)
        if len(prestamos_activos) >= MAX_PRESTAMOS_ACTIVOS:
            raise HTTPException(status_code=409, detail="Limite alcanzado (Maximo 3 activos).")  # Regla 1

        if libro.stock <= 0:
            raise HTTPException(status_code=409, detail="No hay stock del libro.")  # Regla 2

        hoy = date.today()
        prestamo = Prestamo(
            socio_id=socio_id,
            libro_id=libro_id,
            fecha_prestamo=hoy,
            fecha_vencimiento=hoy + timedelta(days=DIAS_PRESTAMO),  # Regla 4
        )
        libro.stock -= 1  # Regla 2

        return self.repo.guardar(prestamo, libro)

    def devolver_prestamo(self, prestamo_id: int) -> Prestamo:
        prestamo = self.repo.get_by_id(prestamo_id)
        if not prestamo:
            raise HTTPException(status_code=404, detail="Prestamo no encontrado.")  # Regla 7

        if prestamo.fecha_devolucion is not None:
            raise HTTPException(status_code=409, detail="El prestamo ya fue devuelto.")  # Regla 6

        hoy = date.today()
        dias_atraso = (hoy - prestamo.fecha_vencimiento).days
        if dias_atraso < 0:
            dias_atraso = 0

        prestamo.fecha_devolucion = hoy
        prestamo.multa = MULTA_POR_DIA * dias_atraso  # Regla 5

        libro = prestamo.libro
        libro.stock += 1  # Regla 5: se repone el stock

        return self.repo.guardar(prestamo, libro)

    def listar_prestamos(self, socio_id: int, activos: Optional[bool] = None) -> Sequence[Prestamo]:
        if not self.socio_repo.get_by_id(socio_id):
            raise HTTPException(status_code=404, detail="Socio no encontrado.")  # Regla 7
        return self.repo.fetch_by_socio(socio_id, activos)
