from database.schema import Contact as DBType

from typing import List
from sqlalchemy.orm import Session

from schema import Contact as Type



async def create(datas: Type, session: Session) -> Type:
    datas = DBType(**dict(datas))
    session.add(datas)
    session.commit()
    session.refresh(datas)
    return datas

async def reads(skip: int, limit: int, session: Session) -> List[Type]:
    results: List[Type] = []
    result = session.query(DBType).offset(skip).limit(limit).all()
    for r in result:
        result = Type.model_validate(r)
        results.append(result)
    return results

async def read(pid: int, session: Session) -> Type:
    return session.query(DBType).filter(DBType.id == pid).first()

async def update(pid: int, datas: Type, session: Session) -> Type | None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        _datas.value = datas.value
        
        session.commit()
        session.refresh(_datas)
    return _datas

async def delete(pid: int, session: Session)  -> Type | None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        session.delete(_datas)
        session.commit()
        session.refresh(_datas)
    return _datas