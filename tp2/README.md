# TP2 - Sistema de Biblioteca (FastAPI + SQLModel)

API REST para gestionar el catálogo de una biblioteca (autores, libros y socios) y sus préstamos.

## Estructura

```
tp2/
├── main.py            # crea la app y registra los routers
├── database.py        # engine de SQLite y sesión
├── models/            # tablas: Autor, Libro, LibroAutor, Socio, Prestamo
├── routers/           # endpoints de cada entidad
├── services/          # reglas de negocio de los préstamos
└── tests/             # pytest con base de datos en memoria
```

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
La base de datos (`biblioteca.db`) se crea sola la primera vez.

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
| POST / GET / PUT / DELETE | `/autores` | Alta, consulta, modificación y baja de autores |
| POST / GET / PUT / DELETE | `/libros` | Ídem para libros (la respuesta incluye sus autores) |
| POST / GET / PUT / DELETE | `/socios` | Ídem para socios |
| POST | `/libros/{id}/autores/{autor_id}` | Asocia un autor a un libro |
| GET | `/libros?disponibles=true` | Libros con stock > 0 |
| POST | `/prestamos` | Registra un préstamo (`socio_id`, `libro_id`) |
| POST | `/prestamos/{id}/devolucion` | Registra la devolución |
| GET | `/socios/{id}/prestamos?activos=true` | Préstamos activos del socio |

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

El stock negativo se rechaza con 422.
