from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    user = None
    if user_id is not None:
        user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(401, "Требуется вход в систему")
    return user
