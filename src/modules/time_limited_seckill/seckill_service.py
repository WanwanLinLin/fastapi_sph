# encoding:utf-8
import asyncio
import schemas
import time
from datetime import datetime, timedelta
from typing import Union

import uvicorn
from fastapi import Depends, status, FastAPI, Header
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils import (verify_jwt_access, success,
                   customize_error_response, get_user_jwt, create_numbering,
                   get_order_code)
from models import time_limited_seckill_goods, seckill_success_users
from sendMessage import send_message

seckill_app = FastAPI()


# 重写HTTPException处理程序
@seckill_app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # return PlainTextResponse(json.dumps(exc.detail), status_code=exc.status_code)
    return JSONResponse(exc.detail, status_code=exc.status_code)


# 提交用户秒杀商品的信息
@seckill_app.post("/v1/seckill/rushPurchase", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, tags=["seckill module"])
async def submit_seckill_order(seckill_info: schemas.SubmitSecKillOrder, username: str = Depends(verify_jwt_access)):
    # 向rabbitmq发送消息
    send_message({"username": username,
                  "goods_name": seckill_info.goods_name,
                  "seckill_price": seckill_info.seckill_price})
    await asyncio.sleep(1)
    remaining_info = time_limited_seckill_goods.find_one({
        "goods_name": seckill_info.goods_name,
        "seckill_price": seckill_info.seckill_price})
    if remaining_info["remaining"] <= 0:
        customize_error_response(code=400,
                                 error_message="Sorry, this item has been sold out!")
    return success("Successful rush purchase! Generating order for you...")


if __name__ == '__main__':
    uvicorn.run(seckill_app, port=6669)
