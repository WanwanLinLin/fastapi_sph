# -*- coding：utf-8 -*-
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, db, username: str):
    user = db.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "code": status.HTTP_404_NOT_FOUND,
            "message": "Users not found",
            "data": None,
            "ok": False

        })
    hashed_password = user["password"]
    if not pwd_context.verify(plain_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={
                                "code": status.HTTP_401_UNAUTHORIZED,
                                "message": "Sorry, the password or username you entered is incorrect",
                                "data": None,
                                "ok": False

                            })
    # 验证成功，返回用户对象和加密后的密码
    return user, hashed_password


def get_password_hash(password):
    return pwd_context.hash(password)


if __name__ == '__main__':
    print(get_password_hash("yyy555"))
