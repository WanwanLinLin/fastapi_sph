# -*- coding：utf-8 -*-
import re
import random
import uvicorn
import schemas

from fastapi import Depends, HTTPException, status, FastAPI
from models import User
from nosql_db import r, r_4
from utils import (verify_password, create_access_token, verify_jwt_access, success,
                   customize_error_response, get_password_hash)
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

users_app = FastAPI()


# 重写HTTPException处理程序
@users_app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # return PlainTextResponse(json.dumps(exc.detail), status_code=exc.status_code)
    return JSONResponse(exc.detail, status_code=exc.status_code)


@users_app.post("/passport/login", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"])
async def login(info: schemas.UserLogin):
    user, hash_password = verify_password(info.password, User, info.username)

    if user:
        # 生成一个JWT并存到redis中
        jwt_access = create_access_token(info.username, hash_password)
        r.setex(info.username, 2 * 60 * 60, jwt_access)

        data = {"nickName": user["name"],
                "name": info.username,
                "userId": user["id"],
                "token": jwt_access}
        return success(data)


# 用户登录成功后获取用户信息的接口
@users_app.get("/passport/auth/getUserInfo", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"])
async def get_user_info(username: str = Depends(verify_jwt_access)):
    user = User.find_one({"username": username})
    data = {
        "id": user["id"],
        "loginName": user["username"],
        "nickName": user["name"],
        "password": user["password"],
        "name": user["username"],
        "phoneNum": user["phone_number"],
        "email": user["email"],
        "headImg": user["headImg"],
        "userLevel": "1"
    }
    return success(data)


# 用户退出登录后清除用户信息的接口
@users_app.get("/passport/logout", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"])
async def logout(username: str = Depends(verify_jwt_access)):
    # r.delete(username)
    return success(None)


# 新用户注册的接口
@users_app.post("/passport/register", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"])
async def register(new_user_info: schemas.UserRegister):
    # 创建一个自增长id
    id_list = list(User.find().sort("id", -1))
    id = id_list[0]["id"] + 1
    # 加密密码
    hash_password = get_password_hash(new_user_info.password)

    info = {"id": id, "username": new_user_info.username,
            "password": hash_password, "name": new_user_info.nick_name,
            "phone_number": new_user_info.phone, "age": new_user_info.age,
            "wallet_address": new_user_info.wallet_address, "email": new_user_info.email}
    # 将新用户插入到数据库中
    User.insert_one(info)

    return success(None)


# 获取注册验证码的接口
@users_app.get("/passport/sendCode/{phone}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"])
async def send_a_code_to_phone(phone: str):
    ret = re.match(r'^1[356789]\d{9}$', phone)
    if not ret:
        customize_error_response(status.HTTP_400_BAD_REQUEST, "Sorry, the phone number format is incorrect!")
    phone_ = User.find_one({"phone_number": phone})
    if phone_:
        customize_error_response(status.HTTP_400_BAD_REQUEST, "Sorry, this mobile number has been registered!")
    # 暂时生成随机验证码
    random_code = "".join([chr(random.randrange(ord('0'), ord('9') + 1)) for _ in range(6)])
    # 使用redis存储随机验证码
    r_4.setex(phone, 60 * 5, random_code)

    return success(random_code)


# 修改用户密码的接口
@users_app.put("/passport/edit_password", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"])
def edit_password(password_info: schemas.ValidateEditPassword, username: str = Depends(verify_jwt_access)):
    # 测试输入的旧密码是否与数据库中的值匹配
    verify_password(plain_password=password_info.password_old, db=User, username=username)
    # 将新密码哈希并存到数据库中
    hash_new_password = get_password_hash(password_info.password_new)
    User.update_one({"username": username}, {"$set": {"password": hash_new_password}})

    return success(None)


# 用于测试JWT的接口
@users_app.get("/testjwt", dependencies=[Depends(verify_jwt_access)])
async def mimi(username: str = Depends(verify_jwt_access)):
    return {
        "message": "token access!",
        "username": username
    }

if __name__ == '__main__':
    uvicorn.run(users_app, port=6667)
