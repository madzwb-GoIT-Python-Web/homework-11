# import configparser
import os
import psycopg2

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

user    = os.environ.get("POSTGRES_USER")
password= os.environ.get("POSTGRES_PASSWORD")
database= os.environ.get("POSTGRES_DB")
domain  = os.environ.get("POSTGRES_DOMAIN")
port    = os.environ.get("POSTGRES_PORT")

# config = configparser.ConfigParser()
# config.read("data/config.ini")

# user    = config.get("DB", "user")
# password= config.get("DB", "password")
# database= config.get("DB", "database")
# domain  = config.get("DB", "domain")
# port    = config.get("DB", "port")

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