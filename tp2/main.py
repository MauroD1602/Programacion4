from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlmodel import Session

from middlewares.auth import JWTAuthMW
from repositories.database import create_db_and_tables, engine
from repositories.seed import seed_bibliotecario, seed_roles_y_permisos
from routers import autor, libro, login, prestamo, socio, usuario

# Se importan todos los modelos para que SQLModel cree todas las tablas
from models.autor import Autor  # noqa: F401
from models.libro import Libro  # noqa: F401
from models.libro_autor import LibroAutor  # noqa: F401
from models.socio import Socio  # noqa: F401
from models.prestamo import Prestamo  # noqa: F401
from models.roles import Rol, Permiso, RolPermiso, UsuarioRol  # noqa: F401
from models.usuario import Usuario  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_roles_y_permisos(session)
        seed_bibliotecario(session)
    yield


jwtAuthMW = JWTAuthMW()

# check_jwt es una dependencia global: exige el token solo en los endpoints marcados con @protected
app = FastAPI(lifespan=lifespan, dependencies=[Depends(jwtAuthMW.check_jwt)])
app.include_router(autor.router)
app.include_router(libro.router)
app.include_router(socio.router)
app.include_router(prestamo.router)
app.include_router(login.router)
app.include_router(usuario.router)


@app.get("/")
async def root():
    return {"message": "API Biblioteca"}
