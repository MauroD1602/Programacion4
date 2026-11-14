# Etapa 5: permisos de los roles "bibliotecario" y "socio"
# `client` es el bibliotecario logueado; `client_socio` es Ana (socio con id 1) logueada.

from sqlmodel import select

from dependencies import get_jwt_service
from models.roles import Permiso, Rol
from services.jwt_service import JWTService

LIBRO = {"titulo": "Otro", "isbn": "999", "stock": 1, "anio": 2000}
AUTOR = {"nombre": "Cortázar", "nacionalidad": "Argentina"}


# Identificación (401)

def test_sin_token_401(client_anonimo):
    assert client_anonimo.get("/libros").status_code == 401


def test_token_invalido_401(client_anonimo):
    respuesta = client_anonimo.get("/libros", headers={"Authorization": "Bearer abc.def.ghi"})
    assert respuesta.status_code == 401


def test_token_vencido_401(client_anonimo, client):
    vencido = JWTService(get_jwt_service().secret_key, expire_minutes=-1)
    token = vencido.create_access_token({"sub": "bibliotecario@gmail.com"})
    respuesta = client_anonimo.get("/libros", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 401


def test_token_de_usuario_inexistente_401(client_anonimo):
    token = get_jwt_service().create_access_token({"sub": "nadie@gmail.com"})
    respuesta = client_anonimo.get("/libros", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 401


def test_esquema_distinto_de_bearer_401(client_anonimo):
    respuesta = client_anonimo.get("/libros", headers={"Authorization": "Basic abc"})
    assert respuesta.status_code == 401


# El socio puede consultar el catálogo

def test_socio_consulta_libros_y_autores(client_socio, libro):
    assert client_socio.get("/libros").status_code == 200
    assert client_socio.get("/libros/1").status_code == 200
    assert client_socio.get("/autores").status_code == 200


# El socio NO puede administrar el catálogo (403)

def test_socio_no_crea_libro_403(client_socio):
    assert client_socio.post("/libros", json=LIBRO).status_code == 403


def test_socio_no_modifica_libro_403(client_socio, libro):
    assert client_socio.put("/libros/1", json=LIBRO).status_code == 403


def test_socio_no_borra_libro_403(client_socio, libro):
    assert client_socio.delete("/libros/1").status_code == 403
    # el libro sigue existiendo
    assert client_socio.get("/libros/1").status_code == 200


def test_socio_no_crea_autor_403(client_socio):
    assert client_socio.post("/autores", json=AUTOR).status_code == 403


def test_socio_no_asocia_autor_403(client, client_socio, libro):
    client.post("/autores", json=AUTOR)
    assert client_socio.post("/libros/1/autores/1").status_code == 403


# El bibliotecario sí puede (caso feliz)

def test_bibliotecario_administra_catalogo(client):
    assert client.post("/autores", json=AUTOR).status_code == 201
    assert client.post("/libros", json=LIBRO).status_code == 201


# Socios y préstamos son del bibliotecario

def test_socio_no_crea_socios_403(client_socio):
    respuesta = client_socio.post("/socios", json={"nombre": "Eva", "email": "eva@gmail.com"})
    assert respuesta.status_code == 403


def test_socio_no_lista_socios_403(client_socio, socio):
    assert client_socio.get("/socios").status_code == 403


def test_socio_no_pide_prestamos_403(client_socio, socio, libro):
    respuesta = client_socio.post("/prestamos", json={"socio_id": 1, "libro_id": 1})
    assert respuesta.status_code == 403


def test_socio_no_registra_devoluciones_403(client, client_socio, socio, libro):
    client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})
    assert client_socio.post("/prestamos/1/devolucion").status_code == 403


# El socio ve únicamente sus préstamos

def test_socio_ve_sus_prestamos(client, client_socio, socio, libro):
    client.post("/socios", json={"nombre": "Beto", "email": "beto@gmail.com"})
    client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})  # de Ana (socio 1)
    client.post("/prestamos", json={"socio_id": 2, "libro_id": 1})  # de Beto (socio 2)

    respuesta = client_socio.get("/socios/1/prestamos?activos=true")
    assert respuesta.status_code == 200
    assert [p["socio_id"] for p in respuesta.json()] == [1]


def test_socio_no_ve_prestamos_de_otro_403(client, client_socio, socio, libro):
    client.post("/socios", json={"nombre": "Beto", "email": "beto@gmail.com"})
    client.post("/prestamos", json={"socio_id": 2, "libro_id": 1})
    assert client_socio.get("/socios/2/prestamos").status_code == 403


def test_bibliotecario_ve_prestamos_de_cualquiera(client, socio, libro):
    client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})
    assert len(client.get("/socios/1/prestamos").json()) == 1


# Los permisos salen de las tablas, no del código

def test_el_403_indica_que_permiso_falta(client_socio):
    respuesta = client_socio.post("/libros", json=LIBRO)
    assert respuesta.status_code == 403
    assert "escribir_catalogo" in respuesta.json()["detail"]


def test_los_permisos_salen_de_la_base(client_socio, session):
    assert client_socio.post("/libros", json=LIBRO).status_code == 403

    # le damos al rol "socio" el permiso de escribir en el catálogo, directo en la base
    rol_socio = session.exec(select(Rol).where(Rol.nombre == "socio")).one()
    permiso = session.exec(select(Permiso).where(Permiso.nombre == "escribir_catalogo")).one()
    rol_socio.permisos.append(permiso)
    session.add(rol_socio)
    session.commit()

    assert client_socio.post("/libros", json=LIBRO).status_code == 201
