from datetime import timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import repositories.auth as repository
import repositories.role as role
from database.connection import db
from schema import Login, LoginResponse, Token, User, Role, EmailRequest

from services.auth  import auth
from services.email import email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

ACCESS_TOKEN_EXPIRE     = 7
REFRESH_TOKEN_EXPIRE    = 60

@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def signup(login: Login, background_tasks: BackgroundTasks, request: Request, session: Session = Depends(db)):
    exist_user = await repository.get_user_by_email(login.email, session)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists.")
    
    login.password = auth.get_password_hash(login.password)
    user = await repository.create_user(login, session)
    response = LoginResponse.model_validate(user)
    person = await repository.get_user_person(user.person_id, session)
    background_tasks.add_task(
        email.send_email,
        user.email,
        " ".join([person.first_name, person.last_name]),
        request.base_url
    )
    return response#{"user": response, "detail": "User successfully created."}


@router.post("/login", response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(db)):
    user = await repository.get_user_by_email(body.username, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    if not auth.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")
    email = user.email
    # Generate JWT
    roles = await repository.get_user_roles(user.id, session)
    if not roles:
        roles += ["user"]
        roles += [user.login]
    if not auth.verify_scopes(body.scopes, roles):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid scope={str(body.scopes)}.")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE)
    access_token_data = {"sub": email, "scope": " ".join(roles)}
    refres_token_data = {"sub": email, "scope": " ".join(roles)}
    access_token = await auth.create_access_token(data=access_token_data, expires_delta=access_token_expires)
    refresh_token = await auth.create_refresh_token(data=refres_token_data, expires_delta=refresh_token_expires)
    await repository.update_token(user, refresh_token, session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), session: Session = Depends(db)):
    token = credentials.credentials
    email = await auth.decode_refresh_token(token)
    user = await repository.get_user_by_email(email, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    await repository.update_token(user, None, session)
    if user.refresh_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    roles = await repository.get_user_roles(user.id, session)
    if not roles:
        roles.append(user.login)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE)
    access_token_data = {"sub": email, "scope": " ".join(roles)}
    refres_token_data = {"sub": email, "scope": " ".join(roles)}
    access_token = await auth.create_access_token(data=access_token_data, expires_delta=access_token_expires)
    refresh_token = await auth.create_refresh_token(data=refres_token_data, expires_delta=refresh_token_expires)
    await repository.update_token(user, refresh_token, session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, session: Session = Depends(db)):
    email = await auth.get_email_from_token(token)
    user = await repository.get_user_by_email(email, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository.confirmed_email(email, session)
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def   request_email(
                body: EmailRequest,
                background_tasks: BackgroundTasks,
                request: Request,
                session: Session = Depends(db)
            ):
    user = await repository.get_user_by_email(body.email, session)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        person = repository.get_user_person(user.person_id, session)
        background_tasks.add_task(
            email.send_email,
            user.email,
            " ".join([person.first_name, person.last_name]),
            request.base_url
        )
    return {"message": "Check your email for confirmation."}