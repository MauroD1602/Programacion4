from services.jwt_service import JWTService
from utils.hash import hash_password, verify_password

CLAVE = "clave-de-prueba-con-mas-de-32-caracteres"
OTRA_CLAVE = "otra-clave-de-prueba-con-mas-de-32-caracteres"


# JWTService

def test_jwt_crea_y_decodifica():
    jwt_service = JWTService(CLAVE)
    token = jwt_service.create_access_token({"sub": "ana@gmail.com"})
    assert jwt_service.decode_token(token)["sub"] == "ana@gmail.com"


def test_jwt_vencido_devuelve_none():
    token = JWTService(CLAVE, expire_minutes=-1).create_access_token({"sub": "ana@gmail.com"})
    assert JWTService(CLAVE).decode_token(token) is None


def test_jwt_con_otra_clave_devuelve_none():
    token = JWTService(CLAVE).create_access_token({"sub": "ana@gmail.com"})
    assert JWTService(OTRA_CLAVE).decode_token(token) is None


def test_jwt_basura_devuelve_none():
    assert JWTService(CLAVE).decode_token("esto-no-es-un-token") is None


# Hash de contraseñas

def test_hash_no_es_la_password():
    assert hash_password("clave123") != "clave123"


def test_verify_password():
    hasheada = hash_password("clave123")
    assert verify_password("clave123", hasheada) is True
    assert verify_password("otra", hasheada) is False
