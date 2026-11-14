from fastapi import APIRouter, HTTPException

from dependencies import JWTServiceDep, LoginServiceDep
from schemas.login import Login, LoginRespuesta

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=LoginRespuesta)
def login(datos: Login, service: LoginServiceDep, jwt_service: JWTServiceDep):
    if not service.login(datos.email, datos.password):
        # el mismo mensaje si falla el email o la contraseña, para no dar pistas
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos.")

    return LoginRespuesta(msg="ok", token=jwt_service.create_access_token({"sub": datos.email}))
