import database.schema as db

from typing import List
from sqlalchemy.orm import Session

from schema import Type



async def create(datas: Type, session: Session) -> Type:
    datas = db.Type(**dict(datas))
    session.add(datas)
    session.commit()
    session.refresh(datas)
    return datas

async def reads(skip: int, limit: int, session: Session) -> List[Type]:
    types: List[Type] = []
    result = session.query(db.Type).offset(skip).limit(limit).all()
    for r in result:
        type = Type.model_validate(r)
        types.append(type)
    return types

async def read(pid: int, session: Session) -> Type:
    return session.query(db.Type).filter(db.Type.id == pid).first()

async def update(pid: int, datas: Type, session: Session) -> Type | None:
    _datas = session.query(db.Type).filter(db.Type.id == pid).first()
    if _datas:
        _datas.name   = datas.name
        session.commit()
    return _datas

async def delete(pid: int, session: Session)  -> Type | None:
    _datas = session.query(db.Type).filter(db.Type.id == pid).first()
    if _datas:
        session.delete(_datas)
        session.commit()
    return _datas