# import configparser
import os
import psycopg2
import redis

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

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()

redis_user    = os.environ.get("REDIS_USER")
# redis_password= os.environ.get("REDIS_PASSWORD")
# redis_database= os.environ.get("REDIS_DB")
redis_domain  = os.environ.get("REDIS_DOMAIN")
redis_port    = os.environ.get("REDIS_PORT")

def get_cache():
    session = redis.from_url(f"redis://{redis_domain}:{redis_port}", db=0)#, decode_responses=True)#, encoding="utf-8"
    try:
        yield session
    finally:
        session.close()
