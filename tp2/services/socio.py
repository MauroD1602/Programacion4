from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException

from models.socio import Socio, SocioBase
from repositories.socio import SocioRepository


class SocioService:
    def __init__(self, repo: Annotated[SocioRepository, Depends()]):
        self.repo = repo

    def get_socios(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        return self.repo.fetch_socios(offset, limit)

    def get_socio(self, socio_id: int) -> Socio:
        socio = self.repo.get_by_id(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado.")  # Regla 7
        return socio

    def create_socio(self, datos: SocioBase) -> Socio:
        if self.repo.get_by_email(datos.email):
            raise HTTPException(status_code=409, detail="El email ya está registrado.")  # Regla 8
        return self.repo.create_socio(datos)

    def update_socio(self, socio_id: int, datos: SocioBase) -> Socio:
        socio = self.get_socio(socio_id)
        if socio.email != datos.email and self.repo.get_by_email(datos.email):
            raise HTTPException(status_code=409, detail="El email ya está registrado.")  # Regla 8
        return self.repo.update_socio(socio, datos)

    def delete_socio(self, socio_id: int) -> None:
        socio = self.get_socio(socio_id)
        if socio.prestamos:
            raise HTTPException(status_code=409, detail="No se puede borrar un socio con préstamos.")
        self.repo.delete_socio(socio)
