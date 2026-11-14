import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

from main import app
from models.roles import Rol
from models.usuario import Usuario
from repositories.database import get_session
from repositories.seed import seed_roles_y_permisos
from utils.hash import hash_password, pwd_context

# bcrypt es lento a propósito; en los tests lo bajamos al mínimo para que la suite corra rápido
pwd_context.update(bcrypt__rounds=4)


@pytest.fixture
def session():
    # Crear base de datos en memoria para probar
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_roles_y_permisos(session)  # los roles y permisos tienen que existir en cada test
        yield session


def crear_cuenta(session, email, rol, socio_id=None, password="clave123"):
    # crea un usuario directo en la base (sin pasar por la API)
    rol_db = session.exec(select(Rol).where(Rol.nombre == rol)).one()
    session.add(Usuario(email=email, password=hash_password(password), socio_id=socio_id, roles=[rol_db]))
    session.commit()


def con_token(client_anonimo, email, password="clave123"):
    # hace login y devuelve un cliente que manda el token en cada pedido
    respuesta = client_anonimo.post("/login", json={"email": email, "password": password})
    token = respuesta.json()["token"]
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def client_anonimo(session):
    # sobrescribo la dependencia get_session para usar la sesión de prueba
    # este cliente no manda token: sirve para probar el login y los 401
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client(session, client_anonimo):
    # cliente logueado como bibliotecario: puede hacerlo todo
    crear_cuenta(session, "bibliotecario@gmail.com", "bibliotecario")
    return con_token(client_anonimo, "bibliotecario@gmail.com")


@pytest.fixture
def socio(client):
    respuesta = client.post("/socios", json={"nombre": "Ana", "email": "ana@gmail.com"})
    return respuesta.json()


@pytest.fixture
def client_socio(session, client_anonimo, socio):
    # cliente logueado como Ana (socio con id 1)
    crear_cuenta(session, "ana@gmail.com", "socio", socio_id=1)
    return con_token(client_anonimo, "ana@gmail.com")


@pytest.fixture
def libro(client):
    respuesta = client.post(
        "/libros", json={"titulo": "Ficciones", "isbn": "111", "stock": 5, "anio": 1944}
    )
    return respuesta.json()
