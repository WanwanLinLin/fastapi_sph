# -*- coding：utf-8 -*-
import re
import time
import random
import uvicorn
import schemas

from typing import Union
from nosql_db import r,r_2, r_4
from models import (Orders, Portfolios, NFT_list, Comments,
                    Portfolios_like, Shipping_address, User, Goods_se_details_sku)
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi import Depends, HTTPException, status, FastAPI, Header
from utils import (verify_password, create_access_token, verify_jwt_access, success,
                   customize_error_response, get_password_hash, get_user_jwt, create_numbering)
from starlette.exceptions import HTTPException as StarletteHTTPException

trade_app = FastAPI()


# 重写HTTPException处理程序
@trade_app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # return PlainTextResponse(json.dumps(exc.detail), status_code=exc.status_code)
    return JSONResponse(exc.detail, status_code=exc.status_code)


# 增加订单的接口
@trade_app.get("/addToCart/{sku_id}/{sku_num}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def add_to_cart(sku_id: str, sku_num: str,
                      userTempId: str = Header(),
                      x_token: Union[str, None] = Header(default=None)):
    # 以下为数据库字段
    sku_id = int(sku_id)
    sku_num = int(sku_num)

    # 第一种情况：用户已经登录
    if x_token:
        # 验证token
        await verify_jwt_access(x_token)
        goods = Goods_se_details_sku.find_one({"id": sku_id})
        default_img = goods["defualtImg"]
        # 订单表与商品表关联的id
        connect_goods_se_sku_id = goods["id"]
        name = goods["skuName"]
        purchase_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        price = int(goods["price"])
        payment = price * sku_num
        order_number = create_numbering(16)
        status = "To_Be_Delivered"

        origin_order = Orders.find_one({"name": name, "userTempId": x_token})
        # 若初始订单存在，则修改订单
        if origin_order:
            # 根据前端要求，返回三种不同的状态
            if sku_num == 1 or sku_num == -1 or sku_num == 0:
                # 删除或增加商品数量时修改产品的总价格
                payment += origin_order["payment"]
                # 删除或增加商品数量时修改产品的总数量
                sku_num += origin_order["purchase_num"]
            else:
                # 删除或增加商品数量时修改产品的总价格
                payment += origin_order["payment"]
                # 删除或增加商品数量时修改产品的总数量
                sku_num += origin_order["purchase_num"]

            Orders.update_one({"name": name, "userTempId": x_token},
                              {"$set": {"purchase_time": purchase_time,
                                        "purchase_num": sku_num,
                                        "price": price,
                                        "payment": payment,
                                        }})

        # 若初始订单不存在，则增加订单
        else:
            Orders.insert_one({"purchase_time": purchase_time,
                               "purchase_num": sku_num,
                               "price": price,
                               "payment": payment,
                               "status": status,
                               "order_number": order_number,
                               "name": name,
                               "connect_goods_se_id": connect_goods_se_sku_id,
                               "userTempId": x_token,
                               "default_img": default_img,
                               "isChecked": 0,
                               "isOrdered": 0,
                               "isCanceled": 0
                               })

        # 将未登录时的购物车合并到已登录的购物车中
        uuid_ = Orders.find_one({"userTempId": userTempId, "name": name})
        token_ = Orders.find_one({"userTempId": x_token, "name": name})
        if uuid_ and token_:
            Orders.update_one({"name": token_["name"], "userTempId": x_token},
                              {"$set": {"purchase_num": token_["purchase_num"] + uuid_["purchase_num"],
                                        "payment": (token_["purchase_num"] + uuid_["purchase_num"]) * token_[
                                            "price"]}})
            # 删除附带uuid的数据
            Orders.delete_one({"name": uuid_["name"], "userTempId": userTempId})

        # 最后将未处理的附带uuid的商品归为已登录的用户所有(标记为token)
        Orders.update_many({"userTempId": userTempId},
                           {"$set": {"userTempId": x_token}})

    # 第二种情况：用户未登录
    else:
        goods = Goods_se_details_sku.find_one({"id": sku_id})
        default_img = goods["defualtImg"]
        # 订单表与商品表关联的id
        connect_goods_se_sku_id = goods["id"]
        name = goods["skuName"]
        purchase_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        price = int(goods["price"])
        payment = price * sku_num
        order_number = create_numbering(16)
        status = "To_Be_Delivered"

        origin_order = Orders.find_one({"name": name, "userTempId": userTempId})
        # 修改原有订单
        if origin_order:
            # 根据前端要求，返回三种不同的状态
            if sku_num == 1 or sku_num == -1 or sku_num == 0:
                # 删除或增加商品数量时修改产品的总价格
                payment += origin_order["payment"]
                # 删除或增加商品数量时修改产品的总数量
                sku_num += origin_order["purchase_num"]
            else:
                # 删除或增加商品数量时修改产品的总价格
                payment += origin_order["payment"]
                # 删除或增加商品数量时修改产品的总数量
                sku_num += origin_order["purchase_num"]

            Orders.update_one({"name": name, "userTempId": userTempId},
                              {"$set": {"purchase_time": purchase_time,
                                        "purchase_num": sku_num,
                                        "price": price,
                                        "payment": payment,
                                        }})

            # 增加订单
        else:
            Orders.insert_one({"purchase_time": purchase_time,
                               "purchase_num": sku_num,
                               "price": price,
                               "payment": payment,
                               "status": status,
                               "order_number": order_number,
                               "name": name,
                               "connect_goods_se_id": connect_goods_se_sku_id,
                               "userTempId": userTempId,
                               "default_img": default_img,
                               "isChecked": 0,
                               "isOrdered": 0,
                               "isCanceled": 0
                               })

    return success(None)


# 查询购物车中订单的接口
@trade_app.get("/cartList", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def query_cart_list(userTempId: str = Header(),
                          x_token: Union[str, None] = Header(default=None)):
    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # 自定义接口要返回的数据格式
    data = [{"cartInfoList": [], "activityRuleList": None, "createTime": create_time}]

    if userTempId and x_token:
        order_info = Orders.find({"userTempId": x_token, "isCanceled": 0}, {"_id": 0, "userTempId": 0})
    else:
        order_info = Orders.find({"userTempId": userTempId, "isCanceled": 0}, {"_id": 0, "userTempId": 0})

    for x in order_info:
        x['price'] = int(x['price'])
        data[0]["cartInfoList"].append(x)

    return success(data)


# 取消订单的接口
@trade_app.delete("/deleteCart/{sku_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def cancel_order_in_cart(sku_id: str, userTempId: str = Header(),
                               x_token: Union[str, None] = Header(default=None)):
    # 已登录的情况
    if userTempId and x_token:
        Orders.update_one({"connect_goods_se_id": int(sku_id),
                           "userTempId": x_token},
                          {"$set": {
                              "isCanceled": 1
                          }})
    # 未登录的情况
    else:
        Orders.update_one({"connect_goods_se_sku_id": int(sku_id),
                           "userTempId": userTempId},
                          {"$set": {
                              "isCanceled": 1
                          }})
    return success(None)


# 切换订单中商品选中状态的接口
@trade_app.get("/checkCart/{sku_id}/{is_checked}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def switch_commodity_selection_status(sku_id: str, is_checked: str,
                                            userTempId: str = Header(),
                                            x_token: Union[str, None] = Header(default=None)):
    if userTempId and x_token:
        Orders.update_one({"connect_goods_se_id": int(sku_id),
                           "userTempId": x_token}
                          , {"$set": {"isChecked": int(is_checked)}})
    else:
        Orders.update_one({"connect_goods_se_id": int(sku_id),
                           "userTempId": userTempId}
                          , {"$set": {"isChecked": int(is_checked)}})

    return success(None)


# 生成并获取订单交易页信息的接口(需要权限认证)
@trade_app.get("/auth/trade", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def get_order_transaction_information(username: str = Depends(verify_jwt_access),
                                            x_token: str = Depends(get_user_jwt)):
    # 定义用户收货地址的空列表
    user_shipping_address: list = []
    # 定义订单详情空列表
    user_order_details: list = []
    # 获取该用户所有的收获地址
    get_user_address = list(Shipping_address.find({"connect_username": username}, {"_id": 0}))
    # 获取该用户所有的订单详情
    get_user_order_details = list(Orders.find({"userTempId": x_token,
                                               "isChecked": 1,
                                               "isOrdered": 0,
                                               "isCanceled": 0
                                               }, {"_id": 0}))
    # 获取用户在数据库中的唯一id
    user_id = User.find_one({"username": username})["id"]
    # 设原始价格为0
    price = 0

    # 自定义每一个响应收货地址
    for each_user_address in get_user_address:
        user_shipping_address.append({
            "id": each_user_address["id"],
            "userAddress": each_user_address["shipping_address"],
            "userId": user_id,
            "consignee": each_user_address["username"],
            "phoneNum": each_user_address["customer_number"],
            "isDefault": each_user_address["isDefault"]
        })

    # 自定义每一个响应订单的详情
    for i, each_order_details in enumerate(get_user_order_details, start=1):
        price += int(each_order_details["payment"])
        user_order_details.append({
            "id": each_order_details["connect_goods_se_id"],
            "orderId": i,
            "skuId": None,
            "skuName": each_order_details["name"],
            "imgUrl": each_order_details["default_img"],
            "orderPrice": each_order_details["payment"],
            "skuNum": each_order_details["purchase_num"],
            "hasStock": True
        })

    # #  生成结算订单后将每条订单的isOrdered字段置为1
    # Orders.update_many({"userTempId": x_token,
    #                     "isChecked": 1,
    #                     "isOrdered": 0,
    #                     "isCanceled": 0},
    #                    {"$set": {"isOrdered": 1}})

    # 整合到data里面
    data = {
        "totalAmount": price,
        "userAddressList": user_shipping_address,
        "tradeNo": create_numbering(24),
        "totalNum": len(user_order_details),
        "detailArrayList": user_order_details
    }

    return success(data)


# 提交订单的接口
@trade_app.post("/auth/submitOrder", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["trade module"])
async def get_order_transaction_information(order_info: schemas.SubmitOrder,
                                            username: str = Depends(verify_jwt_access),
                                            x_token: str = Depends(get_user_jwt),
                                            tradeNo: str = Header()):
    # 如果订单号已经存在，则返回错误信息
    info = r_2.hgetall(tradeNo)
    if info:
        customize_error_response(code=400,
                                 error_message="Sorry, this order number already exists!")

    return


if __name__ == '__main__':
    uvicorn.run(trade_app, port=6668)
