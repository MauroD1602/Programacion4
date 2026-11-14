from typing import Annotated

from fastapi import Depends

from repositories.usuario import UsuarioRepository
from utils.hash import verify_password


class LoginService:
    def __init__(self, repo: Annotated[UsuarioRepository, Depends()]):
        self.repo = repo

    def login(self, email: str, password: str) -> bool:
        usuario = self.repo.get_by_email(email)
        if not usuario:
            return False
        return verify_password(password, usuario.password)
