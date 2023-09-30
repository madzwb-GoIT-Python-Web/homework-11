import os

from fastapi        import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing         import List

import pa_fastapi.repositories.persons as repository

from pa_fastapi.database.connection    import get_db
from pa_fastapi.routes.rates           import *
from pa_fastapi.schema                 import PersonContacts as Type
from pa_fastapi.services.auth          import auth

names = os.path.splitext(os.path.basename(__file__))[0]
name = names.capitalize()
error_not_found = f"{name} not found."

router = APIRouter(prefix=f"/{name}", tags=[name])

@router.get("/", response_model=List[Type])
async def reads_persons(first_name: str = "", last_name: str = "", session: Session = Depends(get_db)):
    _datas = await repository.reads_persons(first_name, last_name, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas

@router.get("/birthday", response_model=List[Type])
async def reads_by_bithday(days: int = 7, session: Session = Depends(get_db)):
    _datas = await repository.reads_persons_by_birthday(days, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas

@router.get("/contacts", response_model=List[Type])
async def reads_contacts(value: str = "", session: Session = Depends(get_db)):
    _datas = await repository.reads_contacts(value, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas

@router.get("/{pid}/contacts", response_model=List[Type])
async def read_contacts(pid: int, session: Session = Depends(get_db)):
    _datas = await repository.read_contacts(pid, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas
