# import pickle
import os
from dotenv import load_dotenv

from datetime import timedelta
# from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter
from starlette.requests import Request
from starlette.responses import Response

from sqlalchemy.orm import Session
from redis import Redis as Cache

import pa_fastapi.repositories.auth    as repository
# import pa_fastapi.repositories.role    as role
# import pa_fastapi.repositories.person  as person

from pa_fastapi.database.connection    import get_db, get_cache
# from pa_fastapi.routes.rates           import *

from pa_fastapi.services.auth  import auth     as auth_service
from pa_fastapi.services.email import email    as email_service

from pa_fastapi.schema import Login, LoginResponse, Token, EmailRequest, Password


router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

# In minutes
ACCESS_TOKEN_EXPIRE         = 7
REFRESH_TOKEN_EXPIRE        = 30
CONFIRM_EMAIL_TOKEN_EXPIRE  = 7*24*60
RESET_PASSWORD_TOKEN_EXPIRE = 7

load_dotenv()
_ratelimiter = os.environ.get("FASTAPI_RATELIMITER")
if _ratelimiter:
    ratelimiter = int(_ratelimiter)
else:
    ratelimiter = False
if not ratelimiter:
    class RateLimiter(RateLimiter):
        async def __call__(self, request: Request, response: Response):
            return

rate_signup = Depends(RateLimiter(times=1, minutes=1))
rate_login  = Depends(RateLimiter(times=1, minutes=1))
rate_op     = Depends(RateLimiter(times=1, seconds=1))

@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED, dependencies=[rate_signup])
async def   signup(
                login: Login,
                background_tasks: BackgroundTasks,
                request : Request,
                session : Session   = Depends(get_db),
                cache   : Cache     = Depends(get_cache)
            ):
    exist_user = await repository.get_user_by_email(login.email, session, cache)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists.")
    
    login.password = auth_service.get_password_hash(login.password)
    user = await repository.create_user(login, session, cache)

    response = LoginResponse.model_validate(user)
    person = await repository.get_user_person(user.person_id, session, cache)
    token = auth_service.create_token({"name": "email", "sub": user.email}, CONFIRM_EMAIL_TOKEN_EXPIRE)
    background_tasks.add_task(
        email_service.send_email,
        user.email,
        " ".join([person.first_name, person.last_name]),
        request.base_url,
        token
    )
    return response#{"user": response, "detail": "User successfully created."}


@router.post("/login", response_model=Token, dependencies=[rate_login])
async def   login(
                body    : OAuth2PasswordRequestForm = Depends(),
                session : Session                   = Depends(get_db),
                cache   : Cache                     = Depends(get_cache)
            ):
    email = body.username
    user = await repository.get_user_by_email(email, session, cache)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")
    # Generate JWT
    roles = await repository.get_user_roles(user.id, session, cache)
    if not roles:
        roles += ["user"]
        roles += [user.login]
    if not auth_service.verify_scopes(body.scopes, roles):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid scope={str(body.scopes)}.")
    
    access_token_expires    = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    refresh_token_expires   = timedelta(minutes=REFRESH_TOKEN_EXPIRE)
    access_token_data = {"name": "access"   , "sub": email, "scope": " ".join(roles)}
    refres_token_data = {"name": "refresh"  , "sub": email, "scope": " ".join(roles)}
    access_token    = await auth_service.create_token(data = access_token_data  , expires_delta = access_token_expires)
    refresh_token   = await auth_service.create_token(data = refres_token_data  , expires_delta = refresh_token_expires)
    await repository.update_refresh_token(user.id, refresh_token, session, cache)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=Token, dependencies=[rate_op])
async def   refresh_token(
                credentials : HTTPAuthorizationCredentials  = Security(security),
                session     : Session                       = Depends(get_db),
                cache       : Cache                         = Depends(get_cache)
            ):
    token = credentials.credentials
    payload = await auth_service.decode_token(token)
    email = payload["sub"]
    user = await repository.get_user_by_email(email, session, cache)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    await repository.update_refresh_token(user.id, None, session, cache)
    if user.refresh_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    roles = await repository.get_user_roles(user.id, session, cache)
    if not roles:
        roles.append(user.login)
    
    access_token_expires    = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    refresh_token_expires   = timedelta(minutes=REFRESH_TOKEN_EXPIRE)
    access_token_data = {"name": "access"   , "sub": email, "scope": " ".join(roles)}
    refres_token_data = {"name": "refresh"  , "sub": email, "scope": " ".join(roles)}
    access_token    = await auth_service.create_token(data = access_token_data  , expires_delta = access_token_expires)
    refresh_token   = await auth_service.create_token(data = refres_token_data  , expires_delta = refresh_token_expires)
    await repository.update_refresh_token(user.id, refresh_token, session, cache)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post('/request_confirm_email', dependencies=[rate_op])
async def   request_email(
                body: EmailRequest,
                background_tasks: BackgroundTasks,
                request : Request,
                session : Session   = Depends(get_db),
                cache   : Cache     = Depends(get_cache)
            ):
    email = body.email
    user = await repository.get_user_by_email(email, session, cache)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is disabled.')

    if user.confirmed:
        return {"message": "Your email is already confirmed."}
    if user:
        token = auth_service.create_token({"name": "email", "sub": user.email}, CONFIRM_EMAIL_TOKEN_EXPIRE)
        person = await repository.get_user_person(user.person_id, session, cache)
        background_tasks.add_task(
            email_service.send_email,
            "Confirm email",
            user.email,
            " ".join([person.first_name, person.last_name]),
            request.base_url,
            token,
            "confirm_email.html"
        )
    return {"message": "Check your email for confirmation."}

@router.post('/request_reset_password', dependencies=[rate_op])
async def   request_reset_password(
                body: EmailRequest,
                background_tasks: BackgroundTasks,
                request : Request,
                session : Session   = Depends(get_db),
                cache   : Cache     = Depends(get_cache)
            ):
    email = body.email
    user = await repository.get_user_by_email(email, session, cache)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is disabled.')
    # if user.disabled:
    #     return {"message": "Your account is disabled."}
    if user:
        token = auth_service.create_token({"name": "reset_password", "sub": user.email}, RESET_PASSWORD_TOKEN_EXPIRE)
        await repository.update_reset_password_token(user.id, token, session, cache)
        person = await repository.get_user_person(user.person_id, session, cache)
        background_tasks.add_task(
            email_service.send_email,
            "Reset password",
            user.email,
            " ".join([person.first_name, person.last_name]),
            request.base_url,
            token,
            "reset_password.html"
        )
    return {"message": "Check your email for password reseting."}


@router.get('/confirm_email/{token}', dependencies=[rate_op])
async def   confirm_email(
                token   : str,
                session : Session   = Depends(get_db),
                cache   : Cache     = Depends(get_cache)
            ):
    email = await auth_service.get_email_from_token(token)
    user = await repository.get_user_by_email(email, session, cache)
    # user = await repository.get_user_by_email(email, session, None)
    
    # if user is None:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Confirmation error.")
    # if token != user.confirm_token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is disabled.')
    
    if user.confirmed:
        return {"message": "Your email is already confirmed."}
    await repository.confirm_email(email, session, cache)
    return {"message": "Email confirmed."}

@router.post('/reset_password', dependencies=[rate_op])
async def   reset_password(
                passwords   : Password,
                token       : str,
                session     : Session   = Depends(get_db),
                cache       : Cache     = Depends(get_cache)
            ):
    email = await auth_service.get_email_from_token(token)
    user = await repository.get_user_by_email(email, session, cache)
    
    # if user is None:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error.")
    if token != user.reset_password_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email.")
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is disabled.')
    
    if passwords.password1 != passwords.password2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwords is not equal.")
    # if user.confirmed:
    #     return {"message": "Your email is already confirmed."}
    # await repository.confirmed_email(email, session)
    await repository.update_reset_password_token(user.id, None, session, cache)
    await repository.update_password(user.id, passwords.password1, session, cache)
    return {"message": "Password reset."}
