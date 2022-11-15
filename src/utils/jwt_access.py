# -*- coding：utf-8 -*-
from typing import Union
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

SECRET_KEY = "wanwanlinlinptyshijbeibasailuoajulia111"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(username: str, password: str):
    payload = {
        "username": username,
        "password": password
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class TokenData(BaseModel):
    username: Union[str, None] = None


# def get_current_user(db: Union[str, None] = None, token: str = Depends(oauth2_scheme)):
def get_current_user(token: str, db: Union[str, None] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        # username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data.username
    # user = db.find_one({"username": token_data.username})
    # if user is None:
    #     raise credentials_exception
    # return user

if __name__ == '__main__':
    from nosql_db import client
    User = client.users.information
    print(create_access_token("Julia", "1234"))
    print(get_current_user("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ikp1bGlhIiwicGFzc3dvcmQiOiIxMjM0In0.MK-PmaOfq44Sc4DPVrU2orFvTv-xEE-SVVdSMUWnyy4"))