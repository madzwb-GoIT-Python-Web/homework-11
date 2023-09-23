from datetime import timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import repositories.auth as repository
from database.connection import db
from schema import Login, LoginResponse, Token, User
from services.auth import auth

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

ACCESS_TOKEN_EXPIRE     = 3
REFRESH_TOKEN_EXPIRE    = 5

@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def signup(login: Login, session: Session = Depends(db)):
    exist_user = await repository.get_user_by_email(login.email, session)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists.")
    
    login.password = auth.get_password_hash(login.password)
    user = await repository.create_user(login, session)
    return {"user": user, "detail": "User successfully created."}


@router.post("/login", response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(db)):
    user = await repository.get_user_by_email(body.username, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    if not auth.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")
    # Generate JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE)
    access_token    = await auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token   = await auth.create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
    await repository.update_token(user, refresh_token, session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), session: Session = Depends(db)):
    token = credentials.credentials
    email = await auth.decode_refresh_token(token)
    user = await repository.get_user_by_email(email, session)
    if user.refresh_token != token:
        await repository.update_token(user, None, session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    access_token    = await auth.create_access_token    (data={"sub": email})
    refresh_token   = await auth.create_refresh_token   (data={"sub": email})
    await repository.update_token(user, refresh_token, session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}