# -*- coding：utf-8 -*-
import re
import random
import uvicorn
import schemas

from models import User
from nosql_db import r, r_4
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi import Depends, HTTPException, status, FastAPI, Header
from utils import (verify_password, create_access_token, verify_jwt_access, success,
                   customize_error_response, get_password_hash, get_user_jwt)
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
async def add_to_cart(sku_id:str, sku_num: str, uuid_: str = Header()):

    pass