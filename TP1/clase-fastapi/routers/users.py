from fastapi import APIRouter, HTTPException, status
from typing import Optional
from models.users import (
    User,
    GetUsersResponse,
    CreateUserResponse,
    DeleteUserResponse,
    UpdateUserResponse
)

router = APIRouter()

usuarios: list[User] = [
    User(id=1, name="juan perez", is_active=True),
    User(id=2, name="pepe sanchez", is_active=False),
]

@router.get("/user")
def get_users(is_active: Optional[bool] = None) -> GetUsersResponse:
    if is_active is not None:
        usuarios_filtrados = [u for u in usuarios if u.is_active == is_active]
        return GetUsersResponse(users=usuarios_filtrados)
    
    r = GetUsersResponse(users=usuarios)
    return r

@router.post("/user")
def create_user(user: User) -> CreateUserResponse:
    usuarios.append(user)
    return CreateUserResponse(message="usuario creado")

@router.put("/user/{id}")
def update_user(id: int, user_actualizado: User) -> UpdateUserResponse:
    for index, user in enumerate(usuarios):
        if user.id == id:
            user_actualizado.id = id  # Mantiene la consistencia del ID
            usuarios[index] = user_actualizado
            return UpdateUserResponse(message="usuario actualizado", user=user_actualizado)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )

@router.delete("/user/{id}")
def delete_user(id: int) -> DeleteUserResponse:
    for user in usuarios:
        if user.id == id:
            usuarios.remove(user)
            return DeleteUserResponse(message="usuario borrado")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )