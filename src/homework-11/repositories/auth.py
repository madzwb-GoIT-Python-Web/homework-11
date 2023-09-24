# from libgravatar import Gravatar
from sqlalchemy.orm import Session

from database.schema import User as DBType
from schema import User as Type
from schema import Login

async def get_user_by_email(email: str, session: Session) -> Type|None:
    result = session.query(DBType).filter(DBType.email == email).first()
    if result:
        return Type.model_validate(result)
    return None

async def create_user(datas: Login, session: Session) -> Type:
    # avatar = None
    # try:
    #     g = Gravatar(body.email)
    #     avatar = g.get_image()
    # except Exception as e:
    #     print(e)
    user = Type(**datas.model_dump())#, avatar=avatar)
    session.add(user)
    session.commit()
    session.refresh(user)
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
