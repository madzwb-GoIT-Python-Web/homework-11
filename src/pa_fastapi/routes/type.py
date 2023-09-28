import os

from fastapi        import APIRouter, HTTPException, Depends, status, Security
from sqlalchemy.orm import Session
from typing         import List

import repositories.type as repository

from database.connection    import get_db, get_cache
from routes.rates           import *
from schema                 import Type as Type
from services.auth          import auth

names = os.path.splitext(os.path.basename(__file__))[0]
name = names[0:-1].capitalize() if names[-1] == 's' else names.capitalize()
error_not_found = f"{name} not found."

router = APIRouter(prefix=f"/{name}", tags=[name])

create_scope    = Security(auth.get_user, scopes=["moder"])
read_scope      = Security(auth.get_user, scopes=["user"])
update_scope    = Security(auth.get_user, scopes=["moder"])
delete_scope    = Security(auth.get_user, scopes=["admin"])

from .common import route
exec(route, globals(), locals())
