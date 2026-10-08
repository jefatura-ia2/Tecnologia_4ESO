import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import config
from ..auth import create_token, current_user, hash_password, verify_password
from ..db import get_db
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
BOARDS = {"pico_w", "esp32_s3"}


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6, max_length=100)
    class_code: str
    group_name: str = Field(default="", max_length=20)
    board: str = "pico_w"


class LoginIn(BaseModel):
    username: str
    password: str


class MeUpdate(BaseModel):
    board: str


def user_out(u: User) -> dict:
    return {"id": u.id, "username": u.username, "full_name": u.full_name, "role": u.role,
            "group_name": u.group_name, "board": u.board}


@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if data.class_code.strip().upper() != config.CLASS_CODE.upper():
        raise HTTPException(400, "Código de clase incorrecto. Pídeselo a tu profesor/a.")
    username = data.username.strip().lower()
    if not re.fullmatch(r"[a-z0-9._-]+", username):
        raise HTTPException(400, "El usuario solo puede tener letras sin tilde, números, punto, guion y guion bajo.")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(400, "Ese nombre de usuario ya existe.")
    board = data.board if data.board in BOARDS else "pico_w"
    user = User(username=username, full_name=data.full_name.strip(), role="student",
                group_name=data.group_name.strip(), board=board, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"token": create_token(user), "user": user_out(user)}


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username.strip().lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Usuario o contraseña incorrectos.")
    return {"token": create_token(user), "user": user_out(user)}


@router.get("/me")
def me(user: User = Depends(current_user)):
    return user_out(user)


@router.patch("/me")
def update_me(data: MeUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if data.board not in BOARDS:
        raise HTTPException(400, "Placa no válida")
    user.board = data.board
    db.add(user)
    db.commit()
    return user_out(user)
