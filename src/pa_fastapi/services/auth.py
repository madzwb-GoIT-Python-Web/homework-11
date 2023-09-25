from __future__ import annotations
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.connection import db

import repositories.auth as repository
from schema import User

class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_HOURS = 24

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def verify_scopes(self, _scopes, scopes_):
        return [scope for scope in _scopes if scope in scopes_ ] if _scopes else True
    
    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: timedelta|None = None):#Optional[float] = None):
        to_encode = data.copy()
        if expires_delta is not None:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"name": "access", "iat": datetime.utcnow(), "exp": expire})#, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: timedelta|None = None):#Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=self.REFRESH_TOKEN_EXPIRE_HOURS)
        to_encode.update({"name": "refresh", "iat": datetime.utcnow(), "exp": expire})#, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["name"] == "refresh":
                email = payload["sub"]
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_user(
            self,
            scopes  : SecurityScopes,
            token   : str     = Depends(oauth2_scheme),
            session : Session = Depends(db)
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
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
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

        user = await repository.get_user_by_email(email, session)
        if user is None:
            raise credentials_exception
        if user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user.")
        return user

    # async def get_active_user(
    #         self,
    #         scopes  : SecurityScopes,
    #         token   : str = Depends(oauth2_scheme),
    #         session : Session = Depends(db)
    #     ):
    #     user = await self.get_user(scopes, token, session)
    #     return user

    # async def get_current_active_user(
    #         self,
    #         scopes  : SecurityScopes,
    #         token   : str       = Depends(oauth2_scheme),
    #         session : Session   = Depends(db)
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