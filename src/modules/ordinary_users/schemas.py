# -*- coding：utf-8 -*-
import re
from nosql_db import r_4
from .models import User
from typing import List, Union, Optional
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException, status


class UserLogin(BaseModel):
    username: str = Field(max_length=15, min_length=3)
    password: str = Field(max_length=30, min_length=3)

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    username: str = Field(max_length=15, min_length=3)
    phone: str

    password: str = Field(max_length=20, min_length=3)
    password1: str = Field(max_length=20, min_length=3)
    nick_name: Union[str, None] = None
    age: Union[str, None] = None
    wallet_address: Union[str, None] = None
    email: Union[str, None] = None
    code: str

    # 确保输入密码与确认密码一致
    @validator("password1")
    def match_password_edit(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Sorry, the entered  password does not match the confirmed password!")
        return v

    @validator("wallet_address")
    def ten_thirty(cls, v):
        if len(v) < 10 or len(v) > 30:
            raise ValueError('Sorry, the wallet address is too long or too short!')
        return v

    @validator("username")
    def no_repeated(cls, v):
        user = User.find_one({"username": v})
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={
                                    "code": status.HTTP_400_BAD_REQUEST,
                                    "message": "Sorry, the user name cannot be duplicate!",
                                    "data": None,
                                    "ok": False

                                })
        return v

    @validator("phone")
    def match_phone_number(cls, v):
        ret = re.match(r'^1[356789]\d{9}$', str(v))
        if not ret:
            raise ValueError("Sorry, the phone number format is incorrect!")
        phone_ = User.find_one({"phone_number": v})
        if phone_:
            raise ValueError("Sorry, this mobile number has been registered!")
        return v

    # 验证用户输入的验证码
    @validator("code")
    def val_code(cls, v, values):
        print(values)
        if "phone" in values:
            if v != r_4.get(values["phone"]):
                # raise ValueError("Sorry, the verification code you entered is incorrect!")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail={
                                        "code": status.HTTP_400_BAD_REQUEST,
                                        "message": "Sorry, the verification code you entered is incorrect!",
                                        "data": None,
                                        "ok": False

                                    })
        return v

    @validator("email")
    def match_email(cls, v):
        ret = re.match(r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$", v)
        if not ret:
            raise ValueError("Sorry, the format of the email account is incorrect!")
        return v.title()
