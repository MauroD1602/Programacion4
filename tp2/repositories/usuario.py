from typing import Optional

from sqlmodel import select

from models.roles import Rol
from models.usuario import Usuario
from repositories.database import SessionDep


class UsuarioRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_email(self, email: str) -> Optional[Usuario]:
        return self.session.exec(select(Usuario).where(Usuario.email == email)).first()

    def create_usuario(self, email: str, password_hash: str, rol: Rol, socio_id: Optional[int] = None) -> Usuario:
        usuario = Usuario(email=email, password=password_hash, socio_id=socio_id, roles=[rol])
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario
