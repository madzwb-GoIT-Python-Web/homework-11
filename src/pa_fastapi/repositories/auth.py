import pickle
# from libgravatar import Gravatar
from sqlalchemy.orm import Session
from redis          import Redis as Cache
from typing import List

# import repositories.user  as user
# import repositories.user  as person
# import repositories.user  as roles
# import repositories.user  as role

from pa_fastapi.database.schema import User as DBUser, Role as DBRole, Roles as DBRoles, Person as DBPerson
# from database.schema import Role, Roles

from pa_fastapi.services.auth import auth
from pa_fastapi.schema import User, Login, UserRoles, Person

from .common import prefix
exec(prefix, globals(), locals())

async def get_user_by_email(email: str, session: Session, cache: Cache|None = None) -> User|None:
    if cache is not None:
        user = cache.get(key(email))
    else:
        user = None
    if user is None:
        user = session.query(DBUser).filter(DBUser.email == email).first()
        if user:
            user = User.model_validate(user)
            if cache is not None:
                cache.set(key(email), pickle.dumps(user))
    else:
        user = pickle.loads(user)
    return user

async def get_user_roles(user_id: int, session: Session, cache: Cache|None = None) -> List[str]:
    records = session.query(DBRoles).join(DBRole).filter(DBRoles.user_id == user_id).all()
    roles: List[str] = []
    for record in records:
        roles.append(record.role.name)
    return roles

async def get_user_person(person_id: int, session: Session, cache: Cache|None = None) -> Person|None:
    person = session.query(DBPerson).filter(DBPerson.id == person_id).first()
    if person:
        return Person.model_validate(person)
    return None

async def create_user(login: Login, session: Session, cache: Cache|None = None) -> User:
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
    model = User.model_validate(user)
    if cache is not None:
        cache.set(key(user.email), pickle.dumps(model))
    return model


async def update_refresh_token(user_id: int, token: str|None, session: Session, cache: Cache|None = None) -> User|None:
    # user.refresh_token = token# if token is not None else ''
    user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if user:
        user.refresh_token = token
        session.commit()
        session.refresh(user)
        model = User.model_validate(user)
        if cache is not None:
            cache.set(key(user.email), pickle.dumps(model))
        return model
    return None

async def update_reset_password_token(user_id: int, token: str|None, session: Session, cache: Cache|None = None) -> User|None:
    # user.refresh_token = token# if token is not None else ''
    user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if user:
        user.reset_password_token = token
        session.commit()
        session.refresh(user)
        model = User.model_validate(user)
        if cache is not None:
            cache.set(key(user.email), pickle.dumps(model))
        return model
    return None

async def confirmed_email(email: str, session: Session, cache: Cache|None = None) -> User|None:
    user = session.query(DBUser).filter(DBUser.email == email).first()
    if user:
        user.confirmed = True
        session.commit()
        session.refresh(user)
        model = User.model_validate(user)
        if cache is not None:
            cache.set(key(user.email), pickle.dumps(model))
        return model
    return None

async def update_password(user_id: int, password: str, session: Session, cache: Cache|None = None) -> User|None:
    user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if user:
        user.password = auth.get_password_hash(password)
        session.commit()
        session.refresh(user)
        model = User.model_validate(user)
        if cache is not None:
            cache.set(key(user.email), pickle.dumps(model))
        return model
    return None
