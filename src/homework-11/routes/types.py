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

from .common import route
exec(route, globals(), locals())

# module = __package__ + ".common"
# if module not in sys.modules:
#     from .common import *
# else:
#     current = os.path.dirname(os.path.realpath(__file__))
#     sys.path.append(current)
#     importlib.reload(sys.modules[module])
