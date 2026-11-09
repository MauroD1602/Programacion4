from datetime import date, timedelta

from models.prestamo import Prestamo


def pedir(client, socio_id, libro_id):
    return client.post("/prestamos/", json={"socio_id": socio_id, "libro_id": libro_id})

def atrasar(session, prestamo_id, dias):
    prestamo = session.get(Prestamo, prestamo_id)
    prestamo.fecha_vencimiento = date.today() - timedelta(days=dias)
    session.add(prestamo)
    session.commit()

# Tests de solicitudes de prestamo

def test_prestamo_ok(client, socio, libro):
    respuesta = pedir(client, 1, 1)
    assert respuesta.status_code == 201
    assert respuesta.json()["fecha_devolucion"] is None

def test_hasta_3_prestamos_activos_ok(client, socio, libro):
    for _ in range(3):
        assert pedir(client, 1, 1).status_code == 201

def test_cuarto_prestamo_409(client, socio, libro):
    for _ in range(3):
        pedir(client, 1, 1)
    assert pedir(client, 1, 1).status_code == 409

def test_devolver_libera_cupo(client, socio, libro):
    for _ in range(3):
        pedir(client, 1, 1)
    client.post("/prestamos/1/devolucion")
    assert pedir(client, 1, 1).status_code == 201

def test_prestar_descuenta_stock(client, socio, libro):
    pedir(client, 1, 1)
    assert client.get("/libros/1").json()["stock"] == 4

def test_sin_stock_409(client, socio):
    client.post("/libros/", json={"titulo": "Agotado", "isbn": "222", "stock": 0, "anio": 2000})
    assert pedir(client, 1, 1).status_code == 409

def test_prestamo_rechazado_no_modifica_el_stock(client, socio, libro):
    for _ in range(3):
        pedir(client, 1, 1)
    pedir(client, 1, 1)  # el cuarto se rechaza
    assert client.get("/libros/1").json()["stock"] == 2

def test_socio_activo_ok(client, socio, libro):
    assert pedir(client, 1, 1).status_code == 201

def test_socio_inactivo_403(client, libro):
    client.post("/socios/", json={"nombre": "Beto", "email": "beto@mail.com", "activo": False})
    assert pedir(client, 1, 1).status_code == 403

def test_vencimiento_14_dias(client, socio, libro):
    prestamo = pedir(client, 1, 1).json()
    esperado = date.today() + timedelta(days=14)
    assert prestamo["fecha_prestamo"] == str(date.today())
    assert prestamo["fecha_vencimiento"] == str(esperado)

def test_prestamo_socio_inexistente_404(client, libro):
    assert pedir(client, 99, 1).status_code == 404

def test_prestamo_libro_inexistente_404(client, socio):
    assert pedir(client, 1, 99).status_code == 404

def test_prestamo_con_datos_incompletos_422(client, socio, libro):
    assert client.post("/prestamos/", json={"socio_id": 1}).status_code == 422

# Tests de devoluciones

def test_devolucion_a_tiempo(client, socio, libro):
    pedir(client, 1, 1)
    respuesta = client.post("/prestamos/1/devolucion")
    assert respuesta.status_code == 200
    assert respuesta.json()["multa"] == 0
    assert respuesta.json()["fecha_devolucion"] == str(date.today())

def test_devolver_repone_stock(client, socio, libro):
    pedir(client, 1, 1)
    client.post("/prestamos/1/devolucion")
    assert client.get("/libros/1").json()["stock"] == 5

def test_multa_100_por_dia_de_atraso(client, session, socio, libro):
    pedir(client, 1, 1)
    atrasar(session, 1, dias=3)
    respuesta = client.post("/prestamos/1/devolucion")
    assert respuesta.json()["multa"] == 300

def test_devolver_el_dia_del_vencimiento_sin_multa(client, session, socio, libro):
    pedir(client, 1, 1)
    atrasar(session, 1, dias=0)
    assert client.post("/prestamos/1/devolucion").json()["multa"] == 0

def test_devolver_dos_veces_409(client, socio, libro):
    pedir(client, 1, 1)
    client.post("/prestamos/1/devolucion")
    assert client.post("/prestamos/1/devolucion").status_code == 409

def test_devolver_prestamo_inexistente_404(client):
    assert client.post("/prestamos/99/devolucion").status_code == 404

def test_listar_prestamos_activos(client, socio, libro):
    pedir(client, 1, 1)
    pedir(client, 1, 1)
    client.post("/prestamos/1/devolucion")

    activos = client.get("/socios/1/prestamos?activos=true").json()
    assert [p["id"] for p in activos] == [2]

    devueltos = client.get("/socios/1/prestamos?activos=false").json()
    assert [p["id"] for p in devueltos] == [1]

    todos = client.get("/socios/1/prestamos").json()
    assert len(todos) == 2

def test_listar_prestamos_inexistentes_404(client):
    assert client.get("/socios/99/prestamos").status_code == 404
