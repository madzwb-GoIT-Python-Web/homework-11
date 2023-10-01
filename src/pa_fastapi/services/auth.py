from __future__ import annotations

import os
# import pickle

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from passlib.context import CryptContext
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from redis          import Redis as Cache

# from typing import Optional

import pa_fastapi.repositories.auth as repository
from pa_fastapi.database.connection import get_db, get_cache
# from pa_fastapi.schema import User
# from services.email import email

class Auth:
    load_dotenv()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    secret_file = os.environ.get("SECRET_KEY_FILE")
    if secret_file:
        with open(secret_file, 'r') as fd:
            SECRET_KEY = ''.join([line.strip() for line in fd.readlines()])
    else:
        SECRET_KEY  = os.environ.get("SECRET_KEY")
    ALGORITHM   = os.environ.get("ALGORITHM")
    
    ACCESS_TOKEN_EXPIRE         = 15
    REFRESH_TOKEN_EXPIRE        = 24*60
    EMAIL_TOKEN_EXPIRE          = 7*24*60
    RESET_PASSWORD_TOKEN_EXPIRE = 15

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def verify_scopes(self, _scopes, scopes_):
        return [scope for scope in _scopes if scope in scopes_ ] if _scopes else True
    
    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    def create_token(self, data: dict, expires_delta: timedelta|None = None):
        to_encode = data.copy()
        if expires_delta is None:
            match data["name"]:
                case "access":
                    expires_delta = self.ACCESS_TOKEN_EXPIRE
                case "refresh":
                    expires_delta = self.REFRESH_TOKEN_EXPIRE
                case "email":
                    expires_delta = self.EMAIL_TOKEN_EXPIRE
                case "reset_password":
                    expires_delta = self.RESET_PASSWORD_TOKEN_EXPIRE
                case _:
                    raise   HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Invalid token name='{data['name']}'."
                            )
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        encoded_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_token

    # def create_email_token(self, data: dict, expires_delta: timedelta|None = None):
    #     to_encode = data.copy()
    #     if expires_delta is not None:
    #         expire = datetime.utcnow() + expires_delta
    #     else:
    #         expire = datetime.utcnow() + timedelta(days=self.EMAIL_TOKEN_EXPIRE_DAYS)
    #     to_encode.update({"name": "email", "iat": datetime.utcnow(), "exp": expire})
    #     encoded_email_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    #     return encoded_email_token

    # def create_reset_password_token(self, data: dict, expires_delta: timedelta|None = None):
    #     to_encode = data.copy()
    #     if expires_delta is not None:
    #         expire = datetime.utcnow() + expires_delta
    #     else:
    #         expire = datetime.utcnow() + timedelta(minutes=self.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)
    #     to_encode.update({"name": "reset_password", "iat": datetime.utcnow(), "exp": expire})
    #     encoded_email_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    #     return encoded_email_token

    async def get_email_from_token(self, token: str):
        try:
            payload = await self.decode_token(token)
            # if "name" in payload and payload["name"] == "email":
            email = payload["sub"]
            return email
            # raise JWTError(f"Ivalid token:{payload}")
        except JWTError as e:
            print(e)
            raise   HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Invalid token."
                    )
        
    # # define a function to generate a new access token
    # async def create_access_token(self, data: dict, expires_delta: timedelta|None = None):
    #     to_encode = data.copy()
    #     if expires_delta is not None:
    #         expire = datetime.utcnow() + expires_delta
    #     else:
    #         expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    #     to_encode.update({"name": "access", "iat": datetime.utcnow(), "exp": expire})
    #     encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    #     return encoded_access_token

    # # define a function to generate a new refresh token
    # async def create_refresh_token(self, data: dict, expires_delta: timedelta|None = None):#Optional[float] = None):
    #     to_encode = data.copy()
    #     if expires_delta:
    #         expire = datetime.utcnow() + expires_delta
    #     else:
    #         expire = datetime.utcnow() + timedelta(hours=self.REFRESH_TOKEN_EXPIRE_HOURS)
    #     to_encode.update({"name": "refresh", "iat": datetime.utcnow(), "exp": expire})#, "scope": "refresh_token"})
    #     encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    #     return encoded_refresh_token

    async def decode_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            # if payload["name"] == "refresh":
            #     email = payload["sub"]
            return payload
            # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token name.')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials.')

    async def get_user(
            self,
            scopes  : SecurityScopes,
            token   : str       = Depends(oauth2_scheme),
            session : Session   = Depends(get_db),
            cache   : Cache     = Depends(get_cache)
        ):
        if scopes.scopes:
            authenticate_value = f'Bearer scope="{scopes.scope_str}"'
        else:
            authenticate_value = "Bearer"
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

        try:
            # Decode JWT
            payload = await self.decode_token(token)
            if payload["name"] == "access":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
                token_scopes = payload["scope"].split()
                if not token_scopes:
                    raise credentials_exception
                if not self.verify_scopes(scopes.scopes, token_scopes):
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository.get_user_by_email(email, session, cache)
        if user is None:
            raise credentials_exception
        if user.disabled:
            raise HTTPException(status_code=400, detail="User is disabled.")
        return user

    # async def get_active_user(
    #         self,
    #         scopes  : SecurityScopes,
    #         token   : str = Depends(oauth2_scheme),
    #         session : Session = Depends(get_db)
    #     ):
    #     user = await self.get_user(scopes, token, session)
    #     return user

    # async def get_current_active_user(
    #         self,
    #         scopes  : SecurityScopes,
    #         token   : str       = Depends(oauth2_scheme),
    #         session : Session   = Depends(get_db)
    #     ):
    #     user = await self.get_active_user(scopes, token, session)
    #     # roles = await repository.get_user_roles(user.id, session)
    #     # if not roles:
    #     #     roles += ["user"]
    #     #     roles += [user.login]
    #     # if not auth.verify_scopes(scopes.scopes, roles):
    #     #     raise HTTPException(
    #     #         status_code=status.HTTP_401_UNAUTHORIZED,
    #     #         detail=f"Access denied. Scopes={str(scopes.scopes)} not match with your scopes={str(roles)}."
    #     #     )
    #     return user

auth = Auth()