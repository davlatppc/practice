from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import UserCreate, UserLogin, UserOut
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, request: Request, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.username == data.username)) is not None:
        raise HTTPException(409, "Такой логин уже занят")
    result = db.execute(
        insert(User).values(username=data.username, password_hash=hash_password(data.password))
    )
    db.commit()
    user_id = result.inserted_primary_key[0]
    request.session["user_id"] = user_id
    return {"id": user_id, "username": data.username}


@router.post("/login", response_model=UserOut)
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Неверный логин или пароль")
    request.session["user_id"] = user.id
    return user


@router.post("/logout", status_code=204)
def logout(request: Request):
    request.session.clear()


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
