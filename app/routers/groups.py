from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Contact, Group, User
from app.schemas import GroupCreate, GroupOut

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("", response_model=list[GroupOut])
def list_groups(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = (
        select(Group.id, Group.name, func.count(Contact.id))
        .outerjoin(Contact, Contact.group_id == Group.id)
        .where(Group.owner_id == user.id)
        .group_by(Group.id)
        .order_by(Group.name)
    )
    return [
        {"id": group_id, "name": name, "contacts_count": count}
        for group_id, name, count in db.execute(stmt)
    ]


@router.post("", response_model=GroupOut, status_code=201)
def create_group(
    data: GroupCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    result = db.execute(insert(Group).values(name=data.name, owner_id=user.id))
    db.commit()
    return {"id": result.inserted_primary_key[0], "name": data.name, "contacts_count": 0}


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    result = db.execute(delete(Group).where(Group.id == group_id, Group.owner_id == user.id))
    if result.rowcount == 0:
        raise HTTPException(404, "Группа не найдена")
    db.commit()
