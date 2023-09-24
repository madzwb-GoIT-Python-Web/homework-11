# import importlib
import os
# import sys

# from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

# import database.schema as schema
# import schema as models

from database.connection import db
from schema import PersonContacts as Type
import repositories.persons as repository

from schema import User
from services.auth import auth

names = os.path.splitext(os.path.basename(__file__))[0]
name = names[0:-1].capitalize() if names[-1] == 's' else names.capitalize()
error_not_found = f"{name} not found."

router = APIRouter(prefix=f"/{name}", tags=[name])

@router.get("/", response_model=List[Type])
async def reads_persons(first_name: str = "", last_name: str = "", session: Session = Depends(db), current_user: User = Depends(auth.get_current_active_user)):
    _datas = await repository.reads_persons(first_name, last_name, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas

@router.get("/birthday", response_model=List[Type])
async def reads_by_bithday(days: int = 7, session: Session = Depends(db), current_user: User = Depends(auth.get_current_active_user)):
    # date = datetime.now() + timedelta(7)
    # date = date.date()
    _datas = await repository.reads_persons_by_birthday(days, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas

# contacts = APIRouter(prefix=f"/contacts", tags=["contacts"])
@router.get("/contacts", response_model=List[Type])
async def reads_contacts(value: str = "", session: Session = Depends(db), current_user: User = Depends(auth.get_current_active_user)):
    _datas = await repository.reads_contacts(value, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas

@router.get("/{pid}/contacts", response_model=List[Type])
async def read_contacts(pid: int, session: Session = Depends(db)):
    _datas = await repository.read_contacts(pid, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas

# module = __package__ + ".common"
# if module not in sys.modules:
#     from .common import *
# else:
#     current = os.path.dirname(os.path.realpath(__file__))
#     sys.path.append(current)
#     importlib.reload(sys.modules[module])

