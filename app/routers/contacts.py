from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, insert, or_, select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Contact, Group, User
from app.schemas import ContactCreate, ContactOut, ContactUpdate

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


def get_own_contact(db: Session, user: User, contact_id: int) -> Contact:
    contact = db.scalar(
        select(Contact).where(Contact.id == contact_id, Contact.owner_id == user.id)
    )
    if contact is None:
        raise HTTPException(404, "Контакт не найден")
    return contact


def check_group(db: Session, user: User, group_id: int | None):
    if group_id is None:
        return
    group = db.scalar(select(Group).where(Group.id == group_id, Group.owner_id == user.id))
    if group is None:
        raise HTTPException(404, "Группа не найдена")


@router.get("", response_model=list[ContactOut])
def list_contacts(
    q: str | None = None,
    group_id: int | None = None,
    birthday_this_month: bool = False,
    sort: Literal["name", "created"] = "name",
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Contact).where(Contact.owner_id == user.id)
    if q:
        stmt = stmt.where(or_(Contact.name.ilike(f"%{q}%"), Contact.phone.ilike(f"%{q}%")))
    if group_id is not None:
        stmt = stmt.where(Contact.group_id == group_id)
    if birthday_this_month:
        month = f"{date.today().month:02d}"
        stmt = stmt.where(func.strftime("%m", Contact.birthday) == month)
    if sort == "name":
        stmt = stmt.order_by(func.lower(Contact.name), Contact.id)
    else:
        stmt = stmt.order_by(Contact.created_at.desc(), Contact.id.desc())
    return db.scalars(stmt.limit(limit).offset(offset)).all()


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(
    contact_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return get_own_contact(db, user, contact_id)


@router.post("", response_model=ContactOut, status_code=201)
def create_contact(
    data: ContactCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    check_group(db, user, data.group_id)
    result = db.execute(insert(Contact).values(**data.model_dump(), owner_id=user.id))
    db.commit()
    return get_own_contact(db, user, result.inserted_primary_key[0])


@router.patch("/{contact_id}", response_model=ContactOut)
def update_contact(
    contact_id: int,
    data: ContactUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_own_contact(db, user, contact_id)
    values = data.model_dump(exclude_unset=True)
    for field in ("name", "phone", "is_favorite"):
        if field in values and values[field] is None:
            del values[field]
    check_group(db, user, values.get("group_id"))
    if values:
        db.execute(
            update(Contact)
            .where(Contact.id == contact_id, Contact.owner_id == user.id)
            .values(**values)
        )
        db.commit()
    return get_own_contact(db, user, contact_id)


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    get_own_contact(db, user, contact_id)
    db.execute(delete(Contact).where(Contact.id == contact_id, Contact.owner_id == user.id))
    db.commit()
