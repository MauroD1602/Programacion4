def test_crear_socio(client):
    respuesta = client.post("/socios/", json={"nombre": "Ana", "email": "ana@gmail.com"})
    assert respuesta.status_code == 201
    assert respuesta.json()["activo"] is True

def test_email_duplicado_409(client, socio):
    respuesta = client.post("/socios/", json={"nombre": "Otra", "email": "ana@gmail.com"})
    assert respuesta.status_code == 409

def test_listar_socios(client, socio):
    assert len(client.get("/socios/").json()) == 1

def test_obtener_socio(client, socio):
    assert client.get("/socios/1").status_code == 200

def test_obtener_socio_inexistente_404(client):
    assert client.get("/socios/99").status_code == 404

def test_modificar_socio(client, socio):
    respuesta = client.put(
        "/socios/1", json={"nombre": "Ana Paz", "email": "ana@gmail.com", "activo": False}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False

def test_modificar_socio_inexistente_404(client):
    respuesta = client.put("/socios/99", json={"nombre": "X", "email": "x@gmail.com"})
    assert respuesta.status_code == 404

def test_modificar_socio_email_duplicado_409(client, socio):
    client.post("/socios/", json={"nombre": "Beto", "email": "beto@gmail.com"})
    respuesta = client.put("/socios/2", json={"nombre": "Beto", "email": "ana@gmail.com"})
    assert respuesta.status_code == 409

def test_borrar_socio(client, socio):
    assert client.delete("/socios/1").status_code == 204
    assert client.get("/socios/1").status_code == 404

def test_borrar_socio_inexistente_404(client):
    assert client.delete("/socios/99").status_code == 404
