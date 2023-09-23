# from libgravatar import Gravatar
from sqlalchemy.orm import Session

from database.schema import User
from schema import Login


async def get_user_by_email(email: str, session: Session) -> User:
    return session.query(User).filter(User.email == email).first()


async def create_user(datas: Login, session: Session) -> User:
    # avatar = None
    # try:
    #     g = Gravatar(body.email)
    #     avatar = g.get_image()
    # except Exception as e:
    #     print(e)
    user = User(**datas.model_dump())#, avatar=avatar)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def update_token(user: User, token: str|None, session: Session) -> User:
    user.refresh_token = token# if token is not None else ''
    session.commit()
    return user