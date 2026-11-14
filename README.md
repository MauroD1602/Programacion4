#TP1: ABM de Usuarios con FastAPI + ABM propio

Clase para aprender **FastAPI** y **Pydantic**.

## Crear el entorno virtual (venv)

Desde esta carpeta (`clase-fastapi`):

```bash
python3 -m venv .venv
```

Activar el entorno virtual:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

## Instalar los requerimientos

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
fastapi dev main.py
```

La API quedará disponible en `http://127.0.0.1:8000` y la documentación interactiva en `http://127.0.0.1:8000/docs`.

## Lint y chequeo de tipos

El proyecto incluye configuración local para dos herramientas:

- **[`setup.cfg`](./setup.cfg)**: configuración de [`pycodestyle`](https://pycodestyle.pycqa.org/) (chequeo de estilo PEP 8). Define `max-line-length = 79` y excluye `.venv` y `__pycache__` del análisis.
- **[`pyrightconfig.json`](./pyrightconfig.json)**: configuración de [`pyright`](https://microsoft.github.io/pyright/) (chequeo de tipos). Apunta al entorno virtual local (`.venv`) para resolver las dependencias instaladas y excluye `.venv` y `__pycache__`.

`pyright` ya está incluido en `requirements.txt`. `pycodestyle` no, así que hay que instalarlo aparte.

Con el entorno virtual activado, correr:

```bash
pip install pycodestyle
python -m pycodestyle .
```

```bash
pyright
```

# TP2 - Sistema de Biblioteca (FastAPI + SQLModel)

API REST para gestionar el catálogo de una biblioteca (autores, libros y socios) y sus préstamos.

## Estructura

```
tp2/
├── main.py            # crea la app, registra los routers y carga los datos iniciales
├── dependencies.py    # alias de dependencias (servicios, JWT) y chequeo de permisos
├── models/            # tablas y clases base: Autor, Libro, Socio, Prestamo, Usuario, Rol, Permiso
├── schemas/           # lo que la API devuelve (respuestas) y datos de login y usuarios
├── routers/           # endpoints: solo traducen HTTP, no tienen reglas
├── services/          # reglas de negocio (las 8 del enunciado) y JWT
├── repositories/      # consultas a la base de datos, sesión y datos iniciales (seed)
├── middlewares/       # @protected y validación del token
├── utils/             # hash de contraseñas
└── tests/             # pytest con base en memoria (api, services, middlewares, repositories)
```

Cada pedido recorre las capas así: **router → service → repository → base de datos**.

- El **router** recibe el pedido HTTP y devuelve la respuesta.
- El **service** aplica las reglas de negocio y decide los errores (404, 403, 409).
- El **repository** es el único que consulta y guarda en la base.

## Cómo correrlo

Todos los comandos se ejecutan **desde la carpeta `tp2`**.

Crear y activar el entorno virtual:

```powershell
# Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Levantar la API:

```bash
fastapi dev main.py
```

La API queda en `http://127.0.0.1:8000` y la documentación interactiva en `http://127.0.0.1:8000/docs`.
La base de datos (`biblioteca.db`) se crea sola la primera vez, junto con un **bibliotecario inicial**:

| Email | Contraseña |
|---|---|
| `bibliotecario@biblioteca.com` | `123456` |

Variables de entorno opcionales (si no se definen, se usan valores de desarrollo):

| Variable | Para qué sirve |
|---|---|
| `JWT_SECRET_KEY` | Clave con la que se firman los tokens (usar una larga y secreta) |
| `BIBLIOTECARIO_PASSWORD` | Contraseña del bibliotecario inicial |

```powershell
# Windows (PowerShell), antes de levantar la API
$env:JWT_SECRET_KEY = "una-clave-larga-y-secreta-de-mas-de-32-caracteres"
```

> Si se hacen cambios en los campos de algún modelo, hay que borrar `biblioteca.db` para que se cree de nuevo con las columnas nuevas.

## Cómo testear

```bash
pytest
```

Con cobertura:

```bash
pytest --cov=. --cov-report=term-missing
```

Los tests usan una base de datos SQLite en memoria, así que no tocan `biblioteca.db`.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST / GET / PUT / DELETE | `/autores` | Alta, consulta (soporta `?offset=&limit=`), modificación y baja de autores |
| POST / GET / PUT / DELETE | `/libros` | Ídem para libros (la respuesta incluye sus autores; soporta `?offset=&limit=`) |
| POST / GET / PUT / DELETE | `/socios` | Ídem para socios (soporta `?offset=&limit=`) |
| POST | `/libros/{id}/autores/{autor_id}` | Asocia un autor a un libro |
| POST | `/login` | Devuelve un token a partir de email y contraseña |
| POST | `/usuarios` | Crea una cuenta de acceso (solo bibliotecario) |
| GET | `/libros?disponibles=true` | Libros con stock > 0 (combinable con `offset` y `limit`) |
| POST | `/prestamos` | Registra un préstamo (`socio_id`, `libro_id`) |
| POST | `/prestamos/{id}/devolucion` | Registra la devolución |
| GET | `/socios/{id}/prestamos?activos=true` | Préstamos activos del socio |

## Autenticación y roles

La API usa **JWT**. El flujo es:

1. `POST /login` con `{"email": "...", "password": "..."}` devuelve un `token` (vence a los 30 minutos).
2. Cada pedido siguiente manda el header `Authorization: Bearer <token>`.
3. En `/docs`, el botón **Authorize** permite pegar el token una sola vez para probar todos los endpoints.

Las contraseñas se guardan hasheadas con bcrypt, nunca en texto plano.

### Cómo se protege cada endpoint

- `@protected` marca el endpoint como protegido. El middleware `JWTAuthMW` (una dependencia global) valida el token de los endpoints marcados y responde **401** si falta, es inválido o venció.
- `permission_check("nombre")` revisa que el usuario tenga ese permiso y responde **403** si no lo tiene.
- Solo `/login` y `/` son públicos.

### Roles y permisos (en tablas)

Un `Usuario` tiene uno o más `Rol`, y cada `Rol` tiene `Permiso`s (tablas `usuariorol` y `rolpermiso`). Se cargan al arrancar la app:

| Permiso | Bibliotecario | Socio |
|---|---|---|
| `leer_catalogo` (GET de autores y libros) | Sí | Sí |
| `escribir_catalogo` (crear, modificar, borrar, asociar autores) | Sí | |
| `administrar_socios` (`/socios`) | Sí | |
| `administrar_prestamos` (`/prestamos`) | Sí | |
| `administrar_usuarios` (`/usuarios`) | Sí | |
| `ver_todos_los_prestamos` | Sí | |
| `ver_prestamos_propios` | | Sí |

Con `/socios/{id}/prestamos`, el bibliotecario ve los de cualquier socio y un socio solo los suyos (si no, 403).

Las cuentas de rol `socio` están vinculadas a un socio mediante `socio_id`. El bibliotecario las crea con `POST /usuarios`:

```json
{"email": "ana@gmail.com", "password": "clave123", "rol": "socio", "socio_id": 1}
```

Si se borra un socio, también se borran sus cuentas de acceso.

## Reglas de negocio

| # | Regla | Error |
|---|---|---|
| 1 | Un socio no puede tener más de 3 préstamos activos | 409 |
| 2 | No se presta un libro sin stock; al prestar se descuenta 1 | 409 |
| 3 | Un socio inactivo no puede pedir préstamos | 403 |
| 4 | El plazo es de 14 días (`fecha_vencimiento = fecha_prestamo + 14 días`) | n/a |
| 5 | Al devolver se repone el stock y se calcula la multa: $100 por día de atraso (0 si llegó a tiempo) | n/a |
| 6 | No se puede devolver un préstamo ya devuelto | 409 |
| 7 | Recurso inexistente | 404 |
| 8 | ISBN o email duplicado | 409 |

Además de las reglas del enunciado:

- El stock negativo se rechaza con `422`.
- Los emails con formato inválido en socios, usuarios y login se rechazan con `422` (`EmailStr`).
- La paginación en `GET /autores`, `GET /libros` y `GET /socios` acepta `offset >= 0` (por defecto `0`) y `1 <= limit <= 100` (por defecto `100`), rechazando valores fuera de rango con `422`.
- No se puede borrar un libro ni un socio que tenga préstamos registrados (`409`).
