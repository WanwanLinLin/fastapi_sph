# -*- coding：utf-8 -*-
import re
import time
import random
import uvicorn
import schemas

from typing import Union
from nosql_db import r, r_4
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
                      userTempId: str = Header(), x_token: Union[str, None] = Header(default=None)):
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
        Orders.update_one({"userTempId": userTempId},
                          {"$set": {"userTempId": x_token}})

    # 第二种情况：用户未登录
    else:
        goods = Goods_se_details_sku.find_one({"id": sku_id})
        default_img = goods["defualtImg"]
        # 订单表与商品表关联的id
        connect_goods_se_sku_id = goods["id"]
        name = goods["skuName"]
        purchase_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        price = goods["price"]
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
                               })

    return success(None)


if __name__ == '__main__':
    uvicorn.run(trade_app, port=6668)
