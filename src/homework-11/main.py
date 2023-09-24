import uvicorn

from fastapi import FastAPI, Path, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
# from sqlalchemy import event

# import database.functions as functions

from database.connection import db, engine
from routes import  auth,       \
                    type,       \
                    contact,    \
                    person,     \
                    persons,    \
                    role

from services.auth import auth as auth_service

app = FastAPI()

# @event.listens_for(engine, 'connect')
# def on_connect(dbapi_connection, connection_record):
#     for name, function in functions.registry.items():
#         dbapi_connection.create_function(name, 1, function)
# async def session(session: Session = Depends(db)):
#     pass

app.include_router(auth.router      , prefix='/api')#, dependencies=[Depends(auth_service.get_current_active_user)])
app.include_router(role.router      , prefix='/api', dependencies=[Depends(auth_service.get_current_active_user)])

app.include_router(persons.router   , prefix='/api', dependencies=[Depends(auth_service.get_current_active_user)])

app.include_router(person.router    , prefix='/api', dependencies=[Depends(auth_service.get_current_active_user)])
app.include_router(contact.router   , prefix='/api', dependencies=[Depends(auth_service.get_current_active_user)])
app.include_router(type.router      , prefix='/api', dependencies=[Depends(auth_service.get_current_active_user)])


@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/healthchecker")
def healthchecker(session: Session = Depends(db)):
    try:
        # Make request
        result = session.execute(text("SELECT * FROM alembic_version")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    # from pathlib import Path
    uvicorn.run(app, host="localhost", port=8000)#, root_path=str(Path.cwd() / "assets"))
