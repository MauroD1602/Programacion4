def test_crear_autor(client):
    respuesta = client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Borges"


def test_listar_autores(client):
    client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    respuesta = client.get("/autores/")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_obtener_autor(client):
    client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    assert client.get("/autores/1").status_code == 200


def test_obtener_autor_inexistente_404(client):
    assert client.get("/autores/99").status_code == 404


def test_modificar_autor(client):
    client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    respuesta = client.put("/autores/1", json={"nombre": "J. L. Borges", "nacionalidad": "Argentina"})
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "J. L. Borges"


def test_modificar_autor_inexistente_404(client):
    respuesta = client.put("/autores/99", json={"nombre": "X", "nacionalidad": "Y"})
    assert respuesta.status_code == 404


def test_borrar_autor(client):
    client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    assert client.delete("/autores/1").status_code == 204
    assert client.get("/autores/1").status_code == 404


def test_borrar_autor_inexistente_404(client):
    assert client.delete("/autores/99").status_code == 404
