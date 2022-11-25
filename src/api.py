# -*- coding：utf-8 -*-
import json
import requests
import uvicorn
from fastapi import FastAPI, status, Depends
# from modules import users_router
from db import Base, engine
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from modules import ValidateList, UserLogin, UserRegister, ValidatePhone, ValidateEditPassword
from utils import verify_jwt_access, get_user_jwt

Base.metadata.create_all(bind=engine)

app = FastAPI()

# 商品管理微服务
GOODS_SERVICE_URL = "http://localhost:6666"

# 用户管理微服务
USERS_SERVICE_URL = "http://localhost:6667"


# 重写HTTPException处理程序
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # return PlainTextResponse(json.dumps(exc.detail), status_code=exc.status_code)
    return JSONResponse(exc.detail, status_code=exc.status_code)


@app.get("/")
async def main():
    return {"message": "There will be a fastapi project"}


# ############################################## 构建商品微服务 ###################################################
# 返回所有类别列表数据(三级联动)的接口
@app.get("/v1/goods/getBaseCategoryList", responses={
    status.HTTP_200_OK: {"description": "Success"}}, tags=["Manage goods module"])
def get_base_category_list():
    result = requests.get(url=f"{GOODS_SERVICE_URL}/getBaseCategoryList")

    return result.json()


# 展示商品列表的接口
@app.post("/v1/goods/list", responses={
    status.HTTP_200_OK: {"description": "Success"}}, tags=["Manage goods module"])
def display_goods_list(goods_info: ValidateList):
    data = {
        "category1Id": goods_info.category1Id,
        "category2Id": goods_info.category2Id,
        "category3Id": goods_info.category3Id,
        "categoryName": goods_info.categoryName,
        "keyword": goods_info.keyword,
        "props": goods_info.props,
        "trademark": goods_info.trademark,
        "order": goods_info.order,
        "pageNo": goods_info.pageNo,
        "pageSize": goods_info.pageSize
    }
    result = requests.post(url=f"{GOODS_SERVICE_URL}/list",
                           json=data)

    return result.json()


# 展示商品详情的接口
@app.get("/v1/goods/item/{sku_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}}, tags=["Manage goods module"])
def show_goods_detail(sku_id: int):
    result = requests.get(url=f"{GOODS_SERVICE_URL}/item/{sku_id}")

    return result.json()


# ############################################## 构建用户微服务 ###################################################
# 用户登录的接口
@app.post("/v1/users/passport/login", responses={
    status.HTTP_200_OK: {"description": "Success"}},
          tags=["users module"])
def login(info: UserLogin):
    data = {
        "username": info.username,
        "password": info.password
    }
    result = requests.post(url=f"{USERS_SERVICE_URL}/passport/login", json=data)

    return result.json()


# 用户登录成功后获取用户信息的接口
@app.get("/v1/users/passport/auth/getUserInfo", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"], dependencies=[Depends(verify_jwt_access)])
async def get_user_info(x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }
    result = requests.get(url=f"{USERS_SERVICE_URL}/passport/auth/getUserInfo",
                          headers=headers)

    return result.json()


# 用户退出登录后清除用户信息的接口
@app.get("/v1/users/passport/logout", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"], dependencies=[Depends(verify_jwt_access)])
async def get_user_info(x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }

    result = requests.get(url=f"{USERS_SERVICE_URL}/passport/logout",
                          headers=headers)

    return result.json()


# 新用户注册的接口
@app.post("/v1/users/passport/register", responses={
    status.HTTP_200_OK: {"description": "Success"}},
          tags=["users module"])
async def register(new_user: UserRegister):
    data = {
        "username": new_user.username,
        "phone": new_user.phone,
        "password": new_user.password,
        "password1": new_user.password1,
        "nick_name": new_user.nick_name,
        "age": new_user.age,
        "wallet_address": new_user.wallet_address,
        "email": new_user.email,
        "code": new_user.code
    }

    result = requests.post(url=f"{USERS_SERVICE_URL}/passport/register", json=data)

    return result.json()


# 修改用户密码的接口
@app.put("/v1/users/passport/edit_password", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["users module"], dependencies=[Depends(verify_jwt_access)])
async def get_user_info(x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }

    result = requests.get(url=f"{USERS_SERVICE_URL}/passport/edit_password",
                          headers=headers)

    return result.json()


# ############################################## 构建交易管理微服务 ###################################################

