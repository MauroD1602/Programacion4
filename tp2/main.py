from fastapi import FastAPI
from database import create_db_and_tables
from contextlib import asynccontextmanager

from models.autor import Autor
from models.libro import Libro
from models.libro_autor import LibroAutor
from models.socio import Socio
from models.prestamo import Prestamo

from routers import autor, libro, socio



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(autor.router)
app.include_router(libro.router)
app.include_router(socio.router)
app.include_router(prestamo.router)

@app.get("/")
async def root():
    return {"message": "API Biblioteca"}
