# import copy
# import inspect
# import os
# import sys
# import types

# from fastapi import APIRouter, HTTPException, Depends, status
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from typing import List

# current = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.dirname(current))

# from database.connection import db
# # from .types import *
# frame = inspect.currentframe()
# while   (                                           \
#                 frame is not None                   \
#             and (frame := frame.f_back)             \
#             and frame.f_code.co_name != "<module>"  \
#         )                                           \
#     or  (                                           \
#                 frame is not None                   \
#             and frame.f_code.co_filename == __file__\
#         )                                           \
# :
#     continue
# mapping = {
#     # "router"    : APIRouter,
#     "Type"      : BaseModel,
#     "repository": type(sys),
#     "name"      : str,
# }
# if frame is not None:
#     module = sys.modules[frame.f_locals["__name__"]]
#     for name, type in mapping.items():
#         value = frame.f_globals[name]
#         setattr(sys.modules[__name__], name, value)
# else:
#     raise ImportError("Can't inject definitions.")

# error_not_found = f"{name} not found."

# if hasattr(__spec__, "_initializing") and __spec__._initializing:
#     begin = list(locals().keys())

route = """
@router.get("/", response_model=List[Type], dependencies=[read_scope])
async def reads(skip: int = 0, limit: int = 100, session: Session = Depends(db)):
    return await repository.reads(skip, limit, session)


@router.get("/{pid}", response_model=Type, dependencies=[read_scope])
async def read(pid: int, session: Session = Depends(db)):
    _datas = await repository.read(pid, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas


@router.post("/", response_model=Type, dependencies=[create_scope])
async def create(model: Type, session: Session = Depends(db)):
    return await repository.create(model, session)


@router.put("/{pid}", response_model=Type, dependencies=[update_scope])
async def update(datas: Type, pid: int, session: Session = Depends(db)):
    _datas = await repository.update(pid, datas, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas


@router.delete("/{pid}", response_model=Type, dependencies=[delete_scope])
async def delete(pid: int, session: Session = Depends(db)):
    _datas = await repository.delete(pid, session)
    if _datas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_not_found)
    return _datas
"""

# if hasattr(__spec__, "_initializing") and __spec__._initializing:
#     end = list(locals().keys())
#     diff = [define for define in end if define not in begin and define != "begin" and not define.startswith('_')]
# # module = sys.modules[frame.f_locals["__name__"]]
# defines = locals()
# for define in diff:
#     func = defines[define]
#     setattr(module, define, types.FunctionType(code = func.__code__, globals = vars(module)))
# pass