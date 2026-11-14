# Las rutas del enunciado se escriben sin barra final (ej. /libros?disponibles=true).
# Estos tests no siguen redirecciones: si alguna ruta redirige (307), el test falla.


def test_rutas_de_consulta_sin_redireccion(client):
    for ruta in ["/autores", "/libros", "/libros?disponibles=true", "/socios"]:
        respuesta = client.get(ruta, follow_redirects=False)
        assert respuesta.status_code == 200, ruta


def test_rutas_de_alta_sin_redireccion(client, socio, libro):
    autor = client.post("/autores", json={"nombre": "Borges", "nacionalidad": "Argentina"}, follow_redirects=False)
    nuevo_libro = client.post(
        "/libros", json={"titulo": "El Aleph", "isbn": "222", "stock": 1, "anio": 1949}, follow_redirects=False
    )
    nuevo_socio = client.post("/socios", json={"nombre": "Beto", "email": "beto@gmail.com"}, follow_redirects=False)
    prestamo = client.post("/prestamos", json={"socio_id": 1, "libro_id": 1}, follow_redirects=False)
    usuario = client.post(
        "/usuarios",
        json={"email": "ana@gmail.com", "password": "clave123", "rol": "socio", "socio_id": 1},
        follow_redirects=False,
    )
    assert [autor.status_code, nuevo_libro.status_code, nuevo_socio.status_code] == [201, 201, 201]
    assert [prestamo.status_code, usuario.status_code] == [201, 201]


def test_docs_publica_el_esquema_de_respuesta():
    from main import app

    esquema = app.openapi()["paths"]["/libros"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert esquema != {}
