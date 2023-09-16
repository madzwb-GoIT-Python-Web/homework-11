import uvicorn

from fastapi import FastAPI, Path, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import db
from routes import persons, contacts, types

app = FastAPI()

app.include_router(persons.persons  , prefix='/api')
app.include_router(persons.contacts , prefix='/api')

app.include_router(persons.router   , prefix='/api')
app.include_router(contacts.router  , prefix='/api')
app.include_router(types.router     , prefix='/api')


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
