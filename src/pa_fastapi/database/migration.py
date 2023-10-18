import os
from pa_fastapi.database.connection import URL

# Perform migration
LOCK = ".lock"
try:
    open(os.path.join(os.getcwd(), LOCK),"r")
except FileNotFoundError as e:
    current = os.path.dirname(os.path.realpath(__file__))
    from alembic.config import Config
    from alembic import command
    config = Config(os.path.join(current,"alembic.ini"))
    config.set_main_option("sqlalchemy.url", URL)
    config.set_main_option("script_location", os.path.join(current,"alembic"))
    command.upgrade(config, "head")
    open(os.path.join(os.getcwd(), LOCK),"w")
