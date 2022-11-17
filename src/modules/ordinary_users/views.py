# -*- coding：utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status
from . import schemas
from .models import User
from nosql_db import r
from utils import verify_password, create_access_token, verify_jwt_access, success

router = APIRouter(
    prefix="/v1/users",
    tags=["users module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/passport/login", responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def login(info: schemas.UserLogin):
    user = verify_password(info.password, User, info.username)
    if user:
        # 生成一个JWT并存到redis中
        jwt_access = create_access_token(info.username, info.password)
        r.setex(info.username, 2 * 60 * 60, jwt_access)

        data = {"nickName": user["name"],
                "name": info.username,
                "userId": user["id"],
                "token": jwt_access}
        return success(data)


# 用户登录成功后获取用户信息的接口
@router.get("/passport/auth/getUserInfo", responses={
    status.HTTP_200_OK: {"description": "Success"}
})
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
@router.get("/passport/logout", responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def logout(username: str = Depends(verify_jwt_access)):
    # r.delete(username)
    return success(None)


# 新用户注册的接口
@router.post("/passport/register", responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def register(new_user_info: schemas.UserRegister):
    # 创建一个自增长id
    id_list = list(User.find().sort("id", -1))
    id = id_list[0]["id"] + 1
    info = {"id": id, "username": new_user_info.username,
            "password": new_user_info.password, "name": new_user_info.nick_name,
            "phone_number": new_user_info.phone, "age": new_user_info.age,
            "wallet_address": new_user_info.wallet_address, "email": new_user_info.email}
    # User.insert_one(info)
    # return success(None)
    return success(info)


@router.get("/testjwt", dependencies=[Depends(verify_jwt_access)])
async def mimi(username: str = Depends(verify_jwt_access)):
    return {
        "message": "token access!",
        "username": username
    }
