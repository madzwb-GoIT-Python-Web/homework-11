from sqlalchemy.orm import Session
from typing import List

from database.schema import User as DBType
from schema import User as Type

from .common import repository
exec(repository, globals(), locals())
