from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from database import get_session

from models.autor import Autor

router = APIRouter(prefix="/autores", tags=["Autores"])

@router.post("/", response_model=Autor, status_code=status.HTTP_201_CREATED)
def create_autor(autor: Autor, session: Session = Depends(get_session)):
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor

@router.get("/", response_model=list[Autor])
def get_autores(autor_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Autor)).all()

@router.get("/{autor_id}", response_model=Autor)
def get_autor(autor_id: int, session: Session = Depends(get_session)):
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado.")
    return autor

@router.put("/{autor_id}", response_model=Autor)
def update_autor(autor_id: int, autor_data: Autor, session: Session = Depends(get_session)):
    autor_db = session.get(Autor, autor_id)
    if not autor_db:
        raise HTTPException(status_code=404, detail="Autor no encontrado.")

    autor_db.nombre = autor_data.nombre
    autor_db.nacionalidad = autor_data.nacionalidad

    session.add(autor_db)
    session.commit()
    session.refresh(autor_db)
    return autor_db

@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_autor(autor_id: int, session: Session = Depends(get_session)):
    autor_db = session.get(Autor, autor_id)
    if not autor_db:
        raise HTTPException(status_code=404, detail="Autor no encontrado.")
    
    session.delete(autor_db)
    session.commit()
    return {"detail": "Autor eliminado"}