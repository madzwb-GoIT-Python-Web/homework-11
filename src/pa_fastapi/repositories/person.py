from redis          import Redis as Cache
from sqlalchemy.orm import Session

from typing import List

from database.schema import Person as DBType
from schema import Person as Type

from .common import repository
exec(repository, globals(), locals())


# async def create(datas: Type, session: Session) -> Type:
#     datas = DBType(**dict(datas))
#     session.add(datas)
#     session.commit()
#     session.refresh(datas)
#     return datas

# async def reads(skip: int, limit: int, session: Session) -> List[Type]:
#     results: List[Type] = []
#     result = session.query(DBType).offset(skip).limit(limit).all()
#     for r in result:
#         result = Type.model_validate(r)
#         results.append(result)
#     return results

# async def read(pid: int, session: Session) -> Type|None:
#     _datas = session.query(DBType).filter(DBType.id == pid).first()
#     if _datas:
#         return  Type.model_validate(_datas)
#     return None

# async def update(pid: int, datas: Type, session: Session) -> Type|None:
#     _datas = session.query(DBType).filter(DBType.id == pid).first()
#     if _datas:
#         values = datas.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
#         for name, value in values.items():
#             if hasattr(_datas, name):
#                 setattr(_datas, name, value)
#         else:
#             session.commit()
#             session.refresh(_datas)
#         return Type.model_validate(_datas)
#     return None

# async def delete(pid: int, session: Session)  -> Type|None:
#     _datas = session.query(DBType).filter(DBType.id == pid).first()
#     if _datas:
#         session.delete(_datas)
#         session.commit()
#         session.refresh(_datas)
#     return _datas
