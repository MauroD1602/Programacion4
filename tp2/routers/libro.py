from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from database import get_session

from models.libro import Libro
from models.autor import Autor

router = APIRouter(prefix="/libros", tags=["Libros"])


def libro_con_autores(libro: Libro):
    datos = libro.model_dump()
    datos["autores"] = [autor.model_dump() for autor in libro.autores]
    return datos


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_libro(libro: Libro, session: Session = Depends(get_session)):
    if libro.stock < 0:
        raise HTTPException(status_code=422, detail="El stock no puede ser negativo.")

    libro_existente = session.exec(select(Libro).where(Libro.isbn == libro.isbn)).first()
    if libro_existente:
        raise HTTPException(status_code=409, detail="El ISBN ya está registrado.")

    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro_con_autores(libro)

@router.get("/")
def get_libros(disponibles: Optional[bool] = None, session: Session = Depends(get_session)):
    query = select(Libro)
    if disponibles is not None:
        if disponibles:
            query = query.where(Libro.stock > 0)
        else:
            query = query.where(Libro.stock == 0)
    libros = session.exec(query).all()
    return [libro_con_autores(libro) for libro in libros]

@router.get("/{libro_id}")
def get_libro(libro_id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    return libro_con_autores(libro)

@router.put("/{libro_id}")
def update_libro(libro_id: int, libro_data: Libro, session: Session = Depends(get_session)):
    libro_db = session.get(Libro, libro_id)
    if not libro_db:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    if libro_data.stock < 0:
        raise HTTPException(status_code=422, detail="El stock no puede ser negativo.")

    if libro_db.isbn != libro_data.isbn:
        isbn_existente = session.exec(select(Libro).where(Libro.isbn == libro_data.isbn)).first()
        if isbn_existente:
            raise HTTPException(status_code=409, detail="El ISBN ya está registrado.")

    libro_db.titulo = libro_data.titulo
    libro_db.isbn = libro_data.isbn
    libro_db.stock = libro_data.stock
    libro_db.anio = libro_data.anio

    session.add(libro_db)
    session.commit()
    session.refresh(libro_db)
    return libro_con_autores(libro_db)

@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_libro(libro_id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    session.delete(libro)
    session.commit()
    return

@router.post("/{libro_id}/autores/{autor_id}")
def asociar_autor_con_libro(libro_id: int, autor_id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado.")

    if autor in libro.autores:
        raise HTTPException(status_code=409, detail="El autor ya está asociado al libro.")

    libro.autores.append(autor)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro_con_autores(libro)