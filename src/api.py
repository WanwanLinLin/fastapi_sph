# -*- coding：utf-8 -*-
from typing import Union

import requests
from fastapi import FastAPI, status, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from db import Base, engine
from modules import (ValidateList, UserLogin, UserRegister, SubmitOrder, SubmitSecKillOrder)
from modules import (admin_user_router, admin_manage_category_router, admin_file_manage_router,
                     admin_manage_sku_router, admin_manage_spu_router, admin_manage_trademark_router)
from setting import Static_PATH
from utils import verify_jwt_access, get_user_jwt

Base.metadata.create_all(bind=engine)

app = FastAPI()
# 配置静态文件
app.mount("/static", StaticFiles(directory=Static_PATH), name="static")

# 注册管理员路由
app.include_router(admin_user_router)
app.include_router(admin_manage_category_router)
app.include_router(admin_file_manage_router)
app.include_router(admin_manage_sku_router)
app.include_router(admin_manage_spu_router)
app.include_router(admin_manage_trademark_router)

"""
用127.0.0.1要比localhost快得多
"""

# 商品管理微服务
GOODS_SERVICE_URL = "http://127.0.0.1:6666/v1/goods"

# 用户管理微服务
USERS_SERVICE_URL = "http://127.0.0.1:6667/v1/users"

# 商品交易管理微服务
TRADE_SERVICE_URL = "http://127.0.0.1:6668/v1/goods"

# 商品秒杀管理微服务
GOODS_SECKILL_URL = "http://127.0.0.1:6669/v1/seckill"


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

# 增加订单的接口
@app.get("/v1/goods/addToCart/{sku_id}/{sku_num}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def add_to_cart(sku_id: str, sku_num: str,
                      userTempId: str = Header(),
                      x_token: Union[str, None] = Header(default=None)):
    headers = {
        "x-token": x_token,
        "userTempId": userTempId
    }

    result = requests.get(url=f"{TRADE_SERVICE_URL}/addToCart/{sku_id}/{sku_num}",
                          headers=headers)

    return result.json()


# 查询购物车中订单的接口
@app.get("/v1/goods/cartList", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def query_cart_list(userTempId: str = Header(),
                          x_token: Union[str, None] = Header(default=None)):
    headers = {
        "x-token": x_token,
        "userTempId": userTempId
    }

    result = requests.get(url=f"{TRADE_SERVICE_URL}/cartList",
                          headers=headers)

    return result.json()


# 删除购物车中商品的接口
@app.delete("/v1/goods/deleteCart/{sku_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def cancel_order_in_cart(sku_id: str, userTempId: str = Header(),
                               x_token: Union[str, None] = Header(default=None)):
    headers = {
        "x-token": x_token,
        "userTempId": userTempId
    }

    result = requests.delete(url=f"{TRADE_SERVICE_URL}/deleteCart/{sku_id}",
                             headers=headers)

    return result.json()


# 切换订单中商品选中状态的接口
@app.get("/v1/goods/checkCart/{sku_id}/{is_checked}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def switch_commodity_selection_status(sku_id: str, is_checked: str,
                                            userTempId: str = Header(),
                                            x_token: Union[str, None] = Header(default=None)):
    headers = {
        "x-token": x_token,
        "userTempId": userTempId
    }

    result = requests.get(url=f"{TRADE_SERVICE_URL}/checkCart/{sku_id}/{is_checked}",
                          headers=headers)

    return result.json()


# 生成并获取订单交易页信息的接口(需要权限认证)
@app.get("/v1/goods/auth/trade", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def get_order_transaction_information(x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }

    result = requests.get(url=f"{TRADE_SERVICE_URL}/auth/trade",
                          headers=headers)

    return result.json()


# 提交订单的接口
@app.post("/v1/goods/auth/submitOrder", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def get_order_transaction_information(tradeNo: str,
                                            order_info: SubmitOrder,
                                            x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }

    data = {
        "consignee": order_info.consignee,
        "consigneeTel": order_info.consigneeTel,
        "deliveryAddress": order_info.deliveryAddress,
        "paymentWay": order_info.paymentWay,
        "orderComment": order_info.orderComment,
        "orderDetailList": order_info.orderDetailList
    }

    params_ = {
        "tradeNo": tradeNo
    }

    result = requests.post(url=f"{TRADE_SERVICE_URL}/auth/submitOrder",
                           headers=headers, params=params_, json=data)

    return result.json()


# 获取订单支付信息的接口
@app.get("/v1/goods/payment/weixin/createNative/{order_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def get_order_payment_info(order_id: str, x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }

    result = requests.get(url=f"{TRADE_SERVICE_URL}/payment/weixin/createNative/{order_id}",
                          headers=headers)

    return result.json()


# 查询订单支付状态的接口
@app.get("/v1/goods/weixin/queryPayStatus/{order_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def check_pay_status(order_id: str, x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }

    result = requests.get(url=f"{TRADE_SERVICE_URL}/weixin/queryPayStatus/{order_id}",
                          headers=headers)

    return result.json()


# 在个人中心展示订单列表的接口
@app.get("/v1/goods/order/auth/{page}/{limit}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def show_order_in_personal_center(page: str, limit: str,
                                        x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }

    result = requests.get(url=f"{TRADE_SERVICE_URL}/order/auth/{page}/{limit}",
                          headers=headers)

    return result.json()


# ############################################## 构建商品秒杀管理微服务 ###################################################

# 用户秒杀商品的接口
@app.post("/v1/seckill/rushPurchase", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["seckill module"])
async def submit_seckill_order(seckill_info: SubmitSecKillOrder, x_token: str = Depends(get_user_jwt)):
    headers = {
        "x-token": x_token
    }
    data = {
        "id": seckill_info.id,
        "goods_name": seckill_info.goods_name,
        "seckill_price": seckill_info.seckill_price
    }

    result = requests.post(url=f"{GOODS_SECKILL_URL}/rushPurchase",
                           headers=headers, json=data)

    return result.json()
