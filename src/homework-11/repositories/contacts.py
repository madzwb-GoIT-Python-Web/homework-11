import database.schema as db

from typing import List
from sqlalchemy.orm import Session

from schema import Contact



async def create(datas: Contact, session: Session) -> Contact:
    datas = db.Contact(**dict(datas))
    session.add(datas)
    session.commit()
    session.refresh(datas)
    return datas

async def reads(skip: int, limit: int, session: Session) -> List[Contact]:
    return session.query(db.Contact).offset(skip).limit(limit).all()

async def read(pid: int, session: Session) -> Contact:
    return session.query(db.Contact).filter(db.Contact.id == pid).first()

async def update(pid: int, datas: Contact, session: Session) -> Contact | None:
    datas = session.query(db.Contact).filter(db.Contact.id == pid).first()
    if datas:
        datas.value = datas.value
        session.commit()
        session.refresh(datas)
    return datas

async def delete(pid: int, session: Session)  -> Contact | None:
    datas = session.query(db.Contact).filter(db.Contact.id == pid).first()
    if datas:
        session.delete(datas)
        session.commit()
        session.refresh(datas)
    return datas