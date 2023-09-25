# import importlib
import os
# import sys

# from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Security
from sqlalchemy.orm import Session
from typing import List

# import schema as models
# import database.schema as schema

from database.connection import db
from schema import Person as Type
import repositories.person as repository

# from schema import User
from services.auth import auth

names = os.path.splitext(os.path.basename(__file__))[0]
name = names[0:-1].capitalize() if names[-1] == 's' else names.capitalize()
error_not_found = f"{name} not found."

router = APIRouter(prefix=f"/{name}", tags=[name])

create_scope    = Security(auth.get_user, scopes=["moder"])
read_scope      = Security(auth.get_user, scopes=["moder"])
update_scope    = Security(auth.get_user, scopes=["moder"])
delete_scope    = Security(auth.get_user, scopes=["admin"])

from .common import route
exec(route, globals(), locals())


# module = __package__ + ".common"
# if module not in sys.modules:
#     from .common import *
# else:
#     current = os.path.dirname(os.path.realpath(__file__))
#     sys.path.append(current)
#     importlib.reload(sys.modules[module])

