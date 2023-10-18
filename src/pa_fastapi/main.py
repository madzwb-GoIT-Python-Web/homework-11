import os
import redis.asyncio as redis
import uvicorn

from dotenv import load_dotenv

from fastapi import FastAPI, Path, Query, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session
from sqlalchemy import text
# from sqlalchemy import event

# import database.functions as functions
import pa_fastapi.database.migration as migration

from pa_fastapi.database.connection import get_db, get_cache
from pa_fastapi.routes import  auth,       \
                                type,       \
                                contact,    \
                                person,     \
                                persons,    \
                                user,       \
                                role,       \
                                pa

from pa_fastapi.services.auth import auth as auth_service

load_dotenv()

app = FastAPI()

_ratelimiter = os.environ.get("FASTAPI_RATELIMITER")
if _ratelimiter:
    ratelimiter = int(_ratelimiter)
else:
    ratelimiter = 0
host = os.environ.get("FASTAPI_HOST")
port = os.environ.get("FASTAPI_PORT")
cache_domain = os.environ.get("REDIS_DOMAIN")
cache_port   = os.environ.get("REDIS_PORT")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{host}:{port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    if ratelimiter:
        r = await redis.Redis(host=cache_domain, port=int(cache_port), db=0, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(r)


# @app.get("/", dependencies=[Depends(RateLimiter(times=1, seconds=1))])
# async def index():
#     return {"msg": "Hello World"}

# @event.listens_for(engine, 'connect')
# def on_connect(dbapi_connection, connection_record):
#     for name, function in functions.registry.items():
#         dbapi_connection.create_function(name, 1, function)
# async def session(session: Session = Depends(get_db)):
#     pass

app.include_router(auth.router      , prefix='/api')

# Personal assistant
app.include_router(pa.router   , prefix='/api', dependencies=[Security(auth_service.get_user, scopes=["user"])])

# Admin helpers
app.include_router(persons.router   , prefix='/api', dependencies=[Security(auth_service.get_user, scopes=["admin"])])

# CRUD
app.include_router(person.router    , prefix='/api')#, dependencies=[Security(auth_service.get_current_active_user, scopes=["admin"])])
app.include_router(contact.router   , prefix='/api')#, dependencies=[Security(auth_service.get_current_active_user, scopes=["admin"])])
app.include_router(type.router      , prefix='/api')#, dependencies=[Security(auth_service.get_current_active_user, scopes=["moder"])])
app.include_router(user.router      , prefix='/api')#, dependencies=[Security(auth_service.get_current_active_user, scopes=["moder"])])
app.include_router(role.router      , prefix='/api')#, dependencies=[Security(auth_service.get_current_active_user, scopes=["moder"])])


@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/healthchecker")
def healthchecker(session: Session = Depends(get_db)):
    try:
        # Make request
        result = session.execute(text("SELECT * FROM alembic_version")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")

def main():
    uvicorn.run(app, host=host, port=int(port))#, root_path=str(Path.cwd() / "assets"))

if __name__ == "__main__":
    # from pathlib import Path
    main()