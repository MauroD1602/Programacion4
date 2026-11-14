import os

from sqlmodel import Session, select

from models.roles import ROL_BIBLIOTECARIO, ROL_SOCIO, Permiso, Rol
from models.usuario import Usuario
from utils.hash import hash_password

# Datos iniciales: roles, permisos y una cuenta de bibliotecario
BIBLIOTECARIO_EMAIL = "bibliotecario@biblioteca.com"
BIBLIOTECARIO_PASSWORD_POR_DEFECTO = "123456"

NOMBRES_PERMISOS = [
    "leer_catalogo",
    "escribir_catalogo",
    "administrar_socios",
    "administrar_prestamos",
    "administrar_usuarios",
    "ver_prestamos_propios",
    "ver_todos_los_prestamos",
]

PERMISOS_POR_ROL = {
    ROL_BIBLIOTECARIO: [
        "leer_catalogo",
        "escribir_catalogo",
        "administrar_socios",
        "administrar_prestamos",
        "administrar_usuarios",
        "ver_todos_los_prestamos",
    ],
    ROL_SOCIO: ["leer_catalogo", "ver_prestamos_propios"],
}


def seed_roles_y_permisos(session: Session) -> None:
    if session.exec(select(Rol)).first():
        return  # ya están cargados

    permisos = {nombre: Permiso(nombre=nombre) for nombre in NOMBRES_PERMISOS}
    session.add_all(permisos.values())
    session.add_all(
        Rol(nombre=rol, permisos=[permisos[p] for p in nombres])
        for rol, nombres in PERMISOS_POR_ROL.items()
    )
    session.commit()


def seed_bibliotecario(session: Session) -> None:
    rol = session.exec(select(Rol).where(Rol.nombre == ROL_BIBLIOTECARIO)).first()
    if rol is None or rol.usuarios:
        return  # faltan los roles, o ya hay un bibliotecario

    password = os.getenv("BIBLIOTECARIO_PASSWORD", BIBLIOTECARIO_PASSWORD_POR_DEFECTO)
    session.add(Usuario(email=BIBLIOTECARIO_EMAIL, password=hash_password(password), roles=[rol]))
    session.commit()
