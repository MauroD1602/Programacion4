from sqlmodel import select

from models.roles import Permiso, Rol
from repositories.seed import seed_roles_y_permisos


def permisos_de(session, nombre_rol):
    rol = session.exec(select(Rol).where(Rol.nombre == nombre_rol)).one()
    return {p.nombre for p in rol.permisos}


def test_se_crean_los_dos_roles(session):
    assert {r.nombre for r in session.exec(select(Rol)).all()} == {"bibliotecario", "socio"}


def test_permisos_del_bibliotecario(session):
    assert permisos_de(session, "bibliotecario") == {
        "leer_catalogo",
        "escribir_catalogo",
        "administrar_socios",
        "administrar_prestamos",
        "administrar_usuarios",
        "ver_todos_los_prestamos",
    }


def test_permisos_del_socio(session):
    assert permisos_de(session, "socio") == {"leer_catalogo", "ver_prestamos_propios"}


def test_el_seed_no_duplica(session):
    seed_roles_y_permisos(session)
    seed_roles_y_permisos(session)
    assert len(session.exec(select(Rol)).all()) == 2
    assert len(session.exec(select(Permiso)).all()) == 7
