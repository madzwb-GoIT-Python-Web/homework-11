# import importlib
import os
# import sys

# from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

# import schema as models
# import database.schema as schema

from database.connection import db
from schema import Person as Type
import repositories.person as repository

# from schema import User
# from services.auth import auth

names = os.path.splitext(os.path.basename(__file__))[0]
name = names[0:-1].capitalize() if names[-1] == 's' else names.capitalize()
error_not_found = f"{name} not found."

router = APIRouter(prefix=f"/{name}", tags=[name])

from .common import route
exec(route, globals(), locals())
