def test_raiz(client):
    assert client.get("/").status_code == 200


def test_crear_libro(client):
    respuesta = client.post(
        "/libros/", json={"titulo": "Ficciones", "isbn": "111", "stock": 5, "anio": 1944}
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["autores"] == []


def test_isbn_duplicado_409(client, libro):  # Regla 8
    respuesta = client.post(
        "/libros/", json={"titulo": "Otro", "isbn": "111", "stock": 1, "anio": 2000}
    )
    assert respuesta.status_code == 409


def test_stock_negativo_422(client):
    respuesta = client.post(
        "/libros/", json={"titulo": "X", "isbn": "999", "stock": -5, "anio": 2000}
    )
    assert respuesta.status_code == 422


def test_obtener_libro(client, libro):
    respuesta = client.get("/libros/1")
    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Ficciones"


def test_obtener_libro_inexistente_404(client):  # Regla 7
    assert client.get("/libros/99").status_code == 404


def test_listar_libros_disponibles(client, libro):
    client.post("/libros/", json={"titulo": "Agotado", "isbn": "222", "stock": 0, "anio": 2000})

    disponibles = client.get("/libros/?disponibles=true").json()
    assert [l["titulo"] for l in disponibles] == ["Ficciones"]

    agotados = client.get("/libros/?disponibles=false").json()
    assert [l["titulo"] for l in agotados] == ["Agotado"]

    assert len(client.get("/libros/").json()) == 2


def test_modificar_libro(client, libro):
    respuesta = client.put(
        "/libros/1", json={"titulo": "Ficciones 2", "isbn": "111", "stock": 9, "anio": 1944}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["stock"] == 9


def test_modificar_libro_inexistente_404(client):  # Regla 7
    respuesta = client.put(
        "/libros/99", json={"titulo": "X", "isbn": "1", "stock": 1, "anio": 2000}
    )
    assert respuesta.status_code == 404


def test_modificar_libro_stock_negativo_422(client, libro):
    respuesta = client.put(
        "/libros/1", json={"titulo": "X", "isbn": "111", "stock": -1, "anio": 1944}
    )
    assert respuesta.status_code == 422


def test_modificar_libro_isbn_duplicado_409(client, libro):  # Regla 8
    client.post("/libros/", json={"titulo": "Otro", "isbn": "222", "stock": 1, "anio": 2000})
    respuesta = client.put(
        "/libros/2", json={"titulo": "Otro", "isbn": "111", "stock": 1, "anio": 2000}
    )
    assert respuesta.status_code == 409


def test_borrar_libro(client, libro):
    assert client.delete("/libros/1").status_code == 204
    assert client.get("/libros/1").status_code == 404


def test_borrar_libro_inexistente_404(client):  # Regla 7
    assert client.delete("/libros/99").status_code == 404


def test_asociar_autor_a_libro(client, libro):
    client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    respuesta = client.post("/libros/1/autores/1")
    assert respuesta.status_code == 200
    assert respuesta.json()["autores"][0]["nombre"] == "Borges"
    # y el libro, al consultarlo, también trae sus autores
    assert client.get("/libros/1").json()["autores"][0]["nombre"] == "Borges"


def test_asociar_autor_ya_asociado_409(client, libro):
    client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    client.post("/libros/1/autores/1")
    assert client.post("/libros/1/autores/1").status_code == 409


def test_asociar_libro_inexistente_404(client):  # Regla 7
    client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    assert client.post("/libros/99/autores/1").status_code == 404


def test_asociar_autor_inexistente_404(client, libro):  # Regla 7
    assert client.post("/libros/1/autores/99").status_code == 404
