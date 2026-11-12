import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session


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
        yield session


@pytest.fixture
def client(session):
    # sobrescribo la dependencia get_session para usar la sesión de prueba
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def socio(client):
    respuesta = client.post("/socios/", json={"nombre": "Ana", "email": "ana@gmail.com"})
    return respuesta.json()


@pytest.fixture
def libro(client):
    respuesta = client.post(
        "/libros/", json={"titulo": "Ficciones", "isbn": "111", "stock": 5, "anio": 1944}
    )
    return respuesta.json()
