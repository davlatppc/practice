import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import BASE_DIR
from app.routers import auth, contacts, groups

SECRET_KEY = os.getenv(
    "SECRET_KEY", "05b304268862bc41392e8b3bcab6b718c82d67387d0d9a5d8057dabe61537740"
)

app = FastAPI(title="Контакты")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(contacts.router)

app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True))
