from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from dependencies import get_jwt_service
from middlewares.auth import JWTAuthMW
from middlewares.protected import protected
from routers import autor, libro, login, prestamo, socio, usuario
from services.jwt_service import JWTService


def crear_app_de_prueba() -> FastAPI:
    # app mínima: un endpoint público y uno marcado con @protected
    app = FastAPI(dependencies=[Depends(JWTAuthMW().check_jwt)])

    @app.get("/publico")
    def publico():
        return {"ok": True}

    @app.get("/privado")
    @protected
    def privado(request: Request):
        return {"sub": request.state.jwt_payload["sub"]}

    return app


client = TestClient(crear_app_de_prueba())


def test_protected_marca_la_funcion():
    def funcion():
        pass

    assert protected(funcion) is funcion
    assert funcion.__protected__ is True


def test_endpoint_publico_no_pide_token():
    assert client.get("/publico").status_code == 200


def test_endpoint_protegido_sin_token_401():
    assert client.get("/privado").status_code == 401


def test_header_sin_bearer_401():
    assert client.get("/privado", headers={"Authorization": "Basic abc"}).status_code == 401


def test_token_invalido_401():
    assert client.get("/privado", headers={"Authorization": "Bearer abc.def.ghi"}).status_code == 401


def test_token_vencido_401():
    vencido = JWTService(get_jwt_service().secret_key, expire_minutes=-1).create_access_token({"sub": "a@a.com"})
    assert client.get("/privado", headers={"Authorization": f"Bearer {vencido}"}).status_code == 401


def test_token_valido_deja_pasar_y_guarda_el_contenido():
    token = get_jwt_service().create_access_token({"sub": "ana@gmail.com"})
    respuesta = client.get("/privado", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 200
    assert respuesta.json() == {"sub": "ana@gmail.com"}


# Guardia: si alguien agrega un endpoint y se olvida del @protected, este test falla.
# Solo /login (y la raíz "/", que está en main.py) son públicos.

def test_todos_los_endpoints_de_los_routers_estan_protegidos():
    for modulo in [autor, libro, socio, prestamo, usuario]:
        for ruta in modulo.router.routes:
            assert getattr(ruta.endpoint, "__protected__", False), f"{ruta.methods} {ruta.path} sin @protected"


def test_login_es_publico():
    for ruta in login.router.routes:
        assert not getattr(ruta.endpoint, "__protected__", False)
