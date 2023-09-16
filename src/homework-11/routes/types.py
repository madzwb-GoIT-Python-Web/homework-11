import importlib
import os
import sys

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from database.connection import db
from schema import Type as Type
import repositories.types as repository


names = os.path.splitext(os.path.basename(__file__))[0]
name = names[0:-1].capitalize() if names[-1] == 's' else names.capitalize()
error_not_found = f"{name} not found."

router = APIRouter(prefix=f"/{name}", tags=[name])

# from .common import route
# exec(route, globals(), locals())

# module = __package__ + ".common"
# if module not in sys.modules:
#     from .common import *
# else:
#     current = os.path.dirname(os.path.realpath(__file__))
#     sys.path.append(current)
#     importlib.reload(sys.modules[module])

@router.get("/", response_model=List[Type])
async def reads(skip: int = 0, limit: int = 100, session: Session = Depends(db)):
    return await repository.reads(skip, limit, session)


@router.get("/{pid}", response_model=Type)
async def read(pid: int, session: Session = Depends(db)):
    _datas = await repository.read(pid, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas


@router.post("/", response_model=Type)
async def create(model: Type, session: Session = Depends(db)):
    return await repository.create(model, session)


@router.put("/{pid}", response_model=Type)
async def update(datas: Type, pid: int, session: Session = Depends(db)):
    _datas = await repository.update(pid, datas, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas


@router.delete("/{pid}", response_model=Type)
async def delete(pid: int, session: Session = Depends(db)):
    _datas = await repository.delete(pid, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas
