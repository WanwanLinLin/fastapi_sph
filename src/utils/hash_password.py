# -*- coding：utf-8 -*-
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, db, username: str):
    user = db.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    hashed_password = user["password"]
    if not pwd_context.verify(plain_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sorry, the password you entered is incorrect")


def get_password_hash(password):
    return pwd_context.hash(password)


if __name__ == '__main__':
    # 测试用的Bob的密码是 "1234"
    x = get_password_hash("1234")
    print(x)
    print(verify_password("1234", x))