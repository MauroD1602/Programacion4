from sqlmodel import select

from models.roles import Rol
from models.usuario import Usuario
from repositories.seed import BIBLIOTECARIO_EMAIL, seed_bibliotecario


def nuevo_usuario(**cambios):
    datos = {"email": "ana@gmail.com", "password": "clave123", "rol": "socio", "socio_id": 1}
    datos.update(cambios)
    return datos


# Crear usuarios (solo el bibliotecario)

def test_bibliotecario_crea_usuario_socio(client, socio):
    respuesta = client.post("/usuarios", json=nuevo_usuario())
    assert respuesta.status_code == 201
    assert [r["nombre"] for r in respuesta.json()["roles"]] == ["socio"]
    assert respuesta.json()["socio_id"] == 1


def test_la_respuesta_no_incluye_la_password(client, socio):
    respuesta = client.post("/usuarios", json=nuevo_usuario())
    assert "password" not in respuesta.json()


def test_usuario_creado_puede_loguearse_y_ver_sus_prestamos(client, client_anonimo, socio, libro):
    client.post("/usuarios", json=nuevo_usuario())
    client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})

    token = client_anonimo.post(
        "/login", json={"email": "ana@gmail.com", "password": "clave123"}
    ).json()["token"]
    respuesta = client_anonimo.get("/socios/1/prestamos", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_bibliotecario_crea_otro_bibliotecario(client):
    datos = nuevo_usuario(email="otro@gmail.com", rol="bibliotecario", socio_id=None)
    respuesta = client.post("/usuarios", json=datos)
    assert respuesta.status_code == 201
    assert respuesta.json()["socio_id"] is None


def test_email_duplicado_409(client, socio):  # Regla 8
    client.post("/usuarios", json=nuevo_usuario())
    assert client.post("/usuarios", json=nuevo_usuario()).status_code == 409


def test_rol_invalido_422(client, socio):
    assert client.post("/usuarios", json=nuevo_usuario(rol="director")).status_code == 422


def test_password_corta_422(client, socio):
    assert client.post("/usuarios", json=nuevo_usuario(password="123")).status_code == 422


def test_rol_socio_sin_socio_id_422(client):
    assert client.post("/usuarios", json=nuevo_usuario(socio_id=None)).status_code == 422


def test_rol_socio_con_socio_inexistente_404(client):  # Regla 7
    assert client.post("/usuarios", json=nuevo_usuario(socio_id=99)).status_code == 404


def test_socio_no_crea_usuarios_403(client_socio):
    datos = nuevo_usuario(email="otra@gmail.com")
    assert client_socio.post("/usuarios", json=datos).status_code == 403


def test_sin_token_no_crea_usuarios_401(client_anonimo):
    assert client_anonimo.post("/usuarios", json=nuevo_usuario()).status_code == 401


# Borrar un socio borra también su cuenta de acceso

def test_borrar_socio_borra_su_cuenta(client, client_anonimo, session, socio):
    client.post("/usuarios", json=nuevo_usuario())
    assert client.delete("/socios/1").status_code == 204
    assert session.exec(select(Usuario).where(Usuario.email == "ana@gmail.com")).first() is None
    respuesta = client_anonimo.post("/login", json={"email": "ana@gmail.com", "password": "clave123"})
    assert respuesta.status_code == 401


# Bibliotecario inicial (se crea al arrancar la app)

def test_bibliotecario_inicial_puede_loguearse(client_anonimo, session):
    seed_bibliotecario(session)
    respuesta = client_anonimo.post(
        "/login", json={"email": BIBLIOTECARIO_EMAIL, "password": "123456"}
    )
    assert respuesta.status_code == 200


def test_bibliotecario_inicial_no_se_duplica(session):
    seed_bibliotecario(session)
    seed_bibliotecario(session)
    assert len(session.exec(select(Usuario)).all()) == 1


def test_rol_que_no_existe_en_la_base_422(client, session, socio):
    # si el rol "socio" no estuviera cargado en la base, no se puede crear la cuenta
    rol = session.exec(select(Rol).where(Rol.nombre == "socio")).one()
    session.delete(rol)
    session.commit()
    assert client.post("/usuarios", json=nuevo_usuario()).status_code == 422
