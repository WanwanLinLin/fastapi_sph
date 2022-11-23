# -*- coding：utf-8 -*-
import redis
from typing import Union
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import status, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from pymongo import mongo_client
from nosql_db import r

SECRET_KEY = "wanwanlinlinptyshijbeibasailuoajulia111"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: Union[str, None] = None


def create_access_token(username: str, password: str):
    payload = {
        "username": username,
        "password": password
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: redis, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": status.HTTP_401_UNAUTHORIZED,
            "message": "Could not validate credentials",
            "data": None,
            "ok": False
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    # 用redis验证token
    user_jwt = db.get(token_data.username)
    if user_jwt is None:
        raise credentials_exception
    return token_data.username


# 作为依赖项，用于验证token
async def verify_jwt_access(x_token: str = Header()):
    username = await get_current_user(r, x_token)
    return username


# 暂时从这里获取token,微服务搭建可能会用到
async def get_user_jwt(x_token: str = Header()):
    # 验证这个token对不对
    await get_current_user(r, x_token)
    return x_token


if __name__ == '__main__':
    pass
