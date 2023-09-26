# from libgravatar import Gravatar
from sqlalchemy.orm import Session
from typing import List

from database.schema import User as DBUser, Role as DBRole, Roles as DBRoles, Person as DBPerson
# from database.schema import Role, Roles
# from schema import User as Type
from schema import User, Login, UserRoles, Person

async def get_user_by_email(email: str, session: Session) -> User|None:
    user = session.query(DBUser).filter(DBUser.email == email).first()
    if user:
        return User.model_validate(user)
    return None

async def get_user_roles(user_id: int, session: Session) -> List[str]:
    results = session.query(DBRoles).join(DBRole).filter(DBRoles.user_id == user_id).all()
    roles: List[str] = []
    for result in results:
        roles.append(result.role.name)
    return roles

async def get_user_person(person_id: int, session: Session) -> Person|None:
    person = session.query(DBPerson).filter(DBPerson.id == person_id).first()
    if person:
        return Person.model_validate(person)
    return None

async def create_user(login: Login, session: Session) -> User:
    # avatar = None
    # try:
    #     g = Gravatar(body.email)
    #     avatar = g.get_image()
    # except Exception as e:
    #     print(e)
    role = session.query(DBRole).filter(DBRole.name == "user").first()
    user_model = User.model_validate(login)
    user = DBUser(**user_model.model_dump())#, avatar=avatar)
    session.add(user)
    session.flush()
    roles = DBRoles(user_id=user.id, role_id=role.id)
    session.add(roles)
    session.flush()
    person_model = Person.model_validate(login)
    person_model.user_id = user.id
    person = DBPerson(**person_model.model_dump())
    session.add(person)
    session.flush()
    user.person_id = person.id
    session.commit()
    return User.model_validate(user)


async def update_token(user: User, token: str|None, session: Session) -> User|None:
    # user.refresh_token = token# if token is not None else ''
    user = session.query(DBUser).filter(DBUser.id == user.id).first()
    if user:
        user.refresh_token = token
        session.commit()
        session.refresh(user)
        return User.model_validate(user)
    return None

async def confirmed_email(email: str, session: Session) -> None:
    user = session.query(DBUser).filter(DBUser.email == email).first()
    if user:
        user.confirmed = True
        session.commit()
