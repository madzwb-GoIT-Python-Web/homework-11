from sqlalchemy.orm import Session
from typing import List

from database.schema import Person as DBType
from schema import Person as Type



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

async def read(pid: int, session: Session) -> Type|None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        return  Type.model_validate(_datas)
    return None

async def update(pid: int, datas: Type, session: Session) -> Type|None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        _datas.first_name   = datas.first_name  if datas.first_name else _datas.first_name
        _datas.last_name    = datas.last_name   if datas.last_name  else _datas.last_name
        _datas.born_date    = datas.born_date   if datas.born_date  else _datas.born_date
        session.commit()
        session.refresh(_datas)
        return Type.model_validate(_datas)
    return None

async def delete(pid: int, session: Session)  -> Type|None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        session.delete(_datas)
        session.commit()
        session.refresh(_datas)
    return _datas
