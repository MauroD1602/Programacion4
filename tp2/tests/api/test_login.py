from sqlmodel import select

from dependencies import get_jwt_service
from models.usuario import Usuario
from tests.conftest import crear_cuenta


def test_login_ok(client_anonimo, session):
    crear_cuenta(session, "ana@gmail.com", "socio")
    respuesta = client_anonimo.post("/login", json={"email": "ana@gmail.com", "password": "clave123"})
    assert respuesta.status_code == 200
    assert respuesta.json()["msg"] == "ok"
    assert respuesta.json()["token"]


def test_el_token_identifica_al_usuario(client_anonimo, session):
    crear_cuenta(session, "ana@gmail.com", "socio")
    token = client_anonimo.post(
        "/login", json={"email": "ana@gmail.com", "password": "clave123"}
    ).json()["token"]
    assert get_jwt_service().decode_token(token)["sub"] == "ana@gmail.com"


def test_login_password_incorrecta_401(client_anonimo, session):
    crear_cuenta(session, "ana@gmail.com", "socio")
    respuesta = client_anonimo.post("/login", json={"email": "ana@gmail.com", "password": "mala"})
    assert respuesta.status_code == 401


def test_login_email_inexistente_401(client_anonimo):
    respuesta = client_anonimo.post("/login", json={"email": "nadie@gmail.com", "password": "clave123"})
    assert respuesta.status_code == 401


def test_login_con_datos_incompletos_422(client_anonimo):
    assert client_anonimo.post("/login", json={"email": "ana@gmail.com"}).status_code == 422


def test_la_password_se_guarda_hasheada(session):
    crear_cuenta(session, "ana@gmail.com", "socio")
    usuario = session.exec(select(Usuario)).first()
    assert usuario.password != "clave123"
    assert usuario.password.startswith("$2")  # prefijo de los hashes bcrypt
