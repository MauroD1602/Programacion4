from sqlmodel import SQLModel
from pydantic import EmailStr


class Login(SQLModel):
    email: EmailStr
    password: str


class LoginRespuesta(SQLModel):
    msg: str
    token: str
