# from libgravatar import Gravatar
from sqlalchemy.orm import Session
from typing import List

from database.schema import User as DBType
from database.schema import Role, Roles
from schema import User as Type
from schema import Login, UserRoles

async def get_user_by_email(email: str, session: Session) -> Type|None:
    result = session.query(DBType).filter(DBType.email == email).first()
    if result:
        return Type.model_validate(result)
    return None

async def get_user_roles(user_id: int, session: Session) -> List[str]:
    result = session.query(Roles).join(Role).filter(Roles.user_id == user_id).all()
    roles: List[str] = []
    for  r in result:
        roles.append(r.role.name)
    return roles

async def create_user(datas: Login, session: Session) -> Type:
    # avatar = None
    # try:
    #     g = Gravatar(body.email)
    #     avatar = g.get_image()
    # except Exception as e:
    #     print(e)
    role = session.query(Role).filter(Role.name == "user").first()
    user = DBType(**datas.model_dump())#, avatar=avatar)
    session.add(user)
    session.commit()
    session.refresh(user)
    roles = Roles(user_id=user.id, role_id=role.id)
    session.add(roles)
    session.commit()
    session.refresh(roles)
    return Type.model_validate(user)


async def update_token(user: Type, token: str|None, session: Session) -> Type|None:
    # user.refresh_token = token# if token is not None else ''
    user = session.query(DBType).filter(DBType.id == user.id).first()
    if user:
        user.refresh_token = token
        session.commit()
        session.refresh(user)
        return Type.model_validate(user)
    return None
