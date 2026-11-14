# TP1 - API REST con FastAPI (Usuarios y Personajes)

API REST desarrollada con **FastAPI** y **Pydantic** como extensión de la primera clase práctica. Gestiona dos recursos en memoria: **usuarios** (`/user`) y **personajes** (`/personaje`), con soporte para operaciones CRUD, filtros por parámetros de consulta y manejo de errores HTTP.

## Estructura

```
TP1/
└── clase-fastapi/
    ├── main.py              # instancia la app de FastAPI y registra los routers
    ├── models/              # modelos Pydantic de entrada y esquemas de respuesta
    │   ├── users.py
    │   └── personajes.py
    ├── routers/             # endpoints y lógica de manejo en memoria
    │   ├── users.py
    │   └── personajes.py
    └── requirements.txt     # dependencias del proyecto
```

## Cómo correrlo

Todos los comandos se ejecutan **desde la carpeta `TP1/clase-fastapi`**.

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

Levantar el servidor de desarrollo:

```bash
fastapi dev main.py
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`.

## Persistencia y datos iniciales

Los datos se almacenan **en memoria** mediante listas de Python (se reinician cada vez que se vuelve a levantar el servidor):

* **Usuarios (`usuarios`):**
  * `id: 1`, `name: "juan perez"`, `is_active: true`
  * `id: 2`, `name: "pepe sanchez"`, `is_active: false`
* **Personajes (`personajes_db`):**
  * `id: 1`, `nombre: "Gimli"`, `raza: "Enano"`, `clase: "Guerrero"`, `nivel: 3`

## Endpoints

### General

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Mensaje de bienvenida de la API |

### Usuarios (`/user`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/user` | Lista todos los usuarios. Acepta filtro opcional `?is_active=true` o `?is_active=false` |
| POST | `/user` | Crea un nuevo usuario (`id`, `name`, `is_active` opcional con valor `true` por defecto) |
| PUT | `/user/{id}` | Actualiza los datos de un usuario existente manteniendo su `id` (`404` si no existe) |
| DELETE | `/user/{id}` | Elimina un usuario por su `id` (`404` si no existe) |

Ejemplo de cuerpo para `POST /user` o `PUT /user/{id}`:

```json
{
  "id": 3,
  "name": "ana gomez",
  "is_active": true
}
```

### Personajes (`/personaje`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/personaje` | Lista todos los personajes. Acepta filtro opcional `?clase=<nombre>` (insensible a mayúsculas/minúsculas) |
| GET | `/personaje/{id}` | Obtiene un personaje por su `id` (`404` si no existe) |
| POST | `/personaje` | Crea un nuevo personaje (`id`, `nombre`, `raza`, `clase`, `nivel`) |
| PUT | `/personaje/{id}` | Actualiza un personaje existente manteniendo su `id` (`404` si no existe) |
| DELETE | `/personaje/{id}` | Elimina un personaje por su `id` (`404` si no existe) |

Ejemplo de cuerpo para `POST /personaje` o `PUT /personaje/{id}`:

```json
{
  "id": 2,
  "nombre": "Legolas",
  "raza": "Elfo",
  "clase": "Arquero",
  "nivel": 4
}
```

## Validaciones y manejo de errores

* **Validación de tipos (`422 Unprocessable Entity`):** FastAPI y Pydantic validan automáticamente que los campos enviados en el body o en la ruta coincidan con los tipos esperados.
* **Recurso no encontrado (`404 Not Found`):** los endpoints `PUT /user/{id}`, `DELETE /user/{id}`, `GET /personaje/{id}`, `PUT /personaje/{id}` y `DELETE /personaje/{id}` devuelven `404` cuando el `id` solicitado no existe.
* **Consistencia de ID en actualizaciones:** en `PUT /user/{id}` y `PUT /personaje/{id}`, se asigna el `id` de la ruta sobre el objeto recibido antes de guardarlo para evitar inconsistencias.

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
