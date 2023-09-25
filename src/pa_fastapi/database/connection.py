import configparser
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

config = configparser.ConfigParser()
config.read("data/config.ini")

user    = config.get("DB", "user")
password= config.get("DB", "password")
database= config.get("DB", "database")
domain  = config.get("DB", "domain")
port    = config.get("DB", "port")

URL = f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/{database}"
engine = create_engine(URL)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def db():
    db = session()
    try:
        yield db
    finally:
        db.close()