import os

from fastapi        import APIRouter, HTTPException, Depends, status, Security
from sqlalchemy.orm import Session
from typing         import List

import pa_fastapi.repositories.contact as contact
import pa_fastapi.repositories.person  as person
import pa_fastapi.repositories.persons as repository
import pa_fastapi.repositories.type    as type

from pa_fastapi.database.connection    import get_db
from pa_fastapi.database.schema        import Person as DBPerson

from pa_fastapi.routes.rates import *

from pa_fastapi.schema import PersonContacts
from pa_fastapi.schema import User, Person, Contact, Type
from pa_fastapi.schema import PAPerson, PAContact

from pa_fastapi.services.auth import auth

names = os.path.splitext(os.path.basename(__file__))[0]
name = names.upper()
error_not_found = f"{name} not found."

router = APIRouter(prefix=f"/{name}", tags=[name])

@router.get("/", response_model=List[PersonContacts])
async def   reads_persons(
                first_name  : str       = "",
                last_name   : str       = "",
                session     : Session   = Depends(get_db),
                user        : User      = Security(auth.get_user, scopes=["user"])
            )\
     :
    _datas = await repository.reads_persons(first_name, last_name, session, user.id)
    if _datas is None:
        raise   HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_not_found
                )
    return _datas

@router.get("/birthday", response_model=List[PersonContacts])
async def   reads_by_bithday(
                days    : int       = 7,
                session : Session   = Depends(get_db),
                user    : User      = Security(auth.get_user, scopes=["user"])
            )\
     :
    _datas = await repository.reads_persons_by_birthday(days, session, user.id)
    if _datas is None:
        raise   HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_not_found
                )
    return _datas

@router.get("/contacts", response_model=List[PersonContacts])
async def   reads_contacts(
                value   : str       = "",
                session : Session   = Depends(get_db),
                user    : User      = Security(auth.get_user, scopes=["user"])
            )\
    :
    _datas = await repository.reads_contacts(value, session, user.id)
    if _datas is None:
        raise   HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_not_found
                )
    return _datas

@router.get("/{pid}/contacts", response_model=List[PersonContacts])
async def   read_contacts(
                pid     : int,
                session : Session   = Depends(get_db),
                user    : User      = Security(auth.get_user, scopes=["user"])
            )\
    :
    _datas = await repository.read_contacts(pid, session, user.id)
    if _datas is None:
        raise   HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_not_found
                )
    return _datas

@router.get("/types", response_model=List[Type])
async def   read_types(
                skip    : int       = 0,
                limit   : int       = 100,
                session : Session   = Depends(get_db),
                user    : User      = Security(auth.get_user, scopes=["user"])
            )\
    :
    return await type.reads(skip, limit, session)



@router.post("/person", response_model=Person)
async def   create_person(
                datas   : PAPerson,
                session : Session   = Depends(get_db),
                user    : User      = Security(auth.get_user, scopes=["user"])
            )\
    :
    _datas = Person.model_validate(datas.model_dump())
    _datas.id = None
    _datas.user_id = user.id
    return await person.create(_datas, session)

@router.put("/person/{pid}", response_model=Contact)
async def   update_person(
                datas   : PAContact,
                pid     : int,
                session : Session = Depends(get_db),
                # user    : User = Security(auth.get_user, scopes=["user"])
            )\
    :
    _datas = Person.model_validate(datas.model_dump())
    _datas.id = pid
    return await person.update(pid, _datas, session)

@router.delete("/person/{pid}", response_model=Contact)
async def   delete_person(
                pid     : int,
                session : Session = Depends(get_db),
                # user = Security(auth.get_user, scopes=["user"])
            )\
    :
    return await person.delete(pid, session)



@router.post("/contact", response_model=Contact)
async def   create_contact(
                datas   : PAContact,
                session : Session = Depends(get_db),
                #   user = Security(auth.get_user, scopes=["user"])
            )\
    :
    _datas = Contact.model_validate(datas.model_dump())
    _datas.id = None
    # _datas.user_id = user.id
    return await contact.create(_datas, session)

@router.put("/contact/{pid}", response_model=Contact)
async def   update_contact(
                datas   : PAContact,
                pid     : int,
                session : Session = Depends(get_db),
                # user = Security(auth.get_user, scopes=["user"])
            )\
    :
    _datas = Contact.model_validate(datas.model_dump())
    _datas.id = pid
    return await contact.update(pid, _datas, session)

@router.delete("/contact/{pid}", response_model=Contact)
async def   delete_contact(
                pid     : int,
                session : Session = Depends(get_db),
                # user = Security(auth.get_user, scopes=["user"])
            )\
    :
    return await contact.delete(pid, session)
