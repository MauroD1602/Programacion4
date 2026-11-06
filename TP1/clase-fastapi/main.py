from fastapi import FastAPI
from routers import users, personajes

# Create the application instance
app = FastAPI()

# Router to user endpoints
app.include_router(users.router)
app.include_router(personajes.router)


# Define a GET route for the root URL
@app.get("/")
def read_root():
    mensaje = "Primer clase de FastAPI"
    return {"message": mensaje}
