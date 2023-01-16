# -*- coding：utf-8 -*-
import os
import time
import math

from . import schemas
from .models import *
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Header
from db import FirstCategory, SecondCategory, ThirdCategory, SessionLocal
from utils import success, customize_error_response, create_numbering, DoubleTokenAccess, TRADEMARK_PATH

session = SessionLocal()
router = APIRouter(
    prefix="/v1/admin/product",
    tags=["manage Trademark module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# 一次性获取所有品牌的接口
@router.get("/baseTrademark/getTrademarkList", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_trademark_list():
    trademark_list = list(Goods_trademark.find({}))
    data = []
    for x_ in trademark_list:
        data.append({
            "id": x_["id"],
            "tmName": x_["tmName"],
            "logoUrl": x_["logoUrl"]
        })

    return success(data)


# 获取品牌总数的接口(需要分页)
@router.get("/baseTrademark/{page}/{limit}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_base_trade_mark(page: str, limit: str):
    page = int(page)
    limit = int(limit)
    trademark_info = list(Goods_trademark.find({}, {"_id": 0}))
    records: List[dict] = []
    for x_ in trademark_info:
        records.append({
            "id": x_["id"],
            "tmName": x_["tmName"],
            "logoUrl": x_["logoUrl"]
        })

    # 该变量用于表示跳过前面多少条
    limit_start = (page - 1) * limit
    # 获取品牌总数量
    total = len(records)
    # 获取实际需要展示的条数
    records = records[limit_start:page * limit]
    # 获取分页总数
    pages = int(math.ceil(total / limit))
    data = {
        "records": records,
        "total": total,
        "size": limit,
        "current": page,
        "searchCount": True,
        "pages": pages
    }

    return success(data)


# 添加品牌的接口
@router.post("/baseTrademark/save", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def save_new_trademark(trade_mark_info: schemas.SaveTrademark):
    id_list = list(Goods_trademark.find().sort("id", -1))
    if id_list:
        id_ = id_list[0]["id"] + 1
    else:
        id_ = 1

    Goods_trademark.insert_one({
        "id": id_,
        "tmName": trade_mark_info.tmName,
        "logoUrl": trade_mark_info.logoUrl
    })

    return success(None)


# 这是更新品牌信息的接口
@router.post("/baseTrademark/update", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def update_trademark(trademark_info: schemas.UpdateTrademark):
    # 更新对应的品牌信息
    Goods_trademark.update_one({"id": id},
                               {"$set": {"tmName": trademark_info.tmName, "logoUrl": trademark_info.logoUrl}})

    return success(None)


# 删除品牌的接口
@router.delete("/baseTrademark/remove/{id_}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def remove_trademark(id_: int):
    trademark_info = Goods_trademark.find_one({"id": id_})
    if not trademark_info:
        customize_error_response(code=400,
                                 error_message="Sorry, the brand does not exist!!")
    # 删除品牌名字段
    Goods_trademark.delete_one({"id": id_})
    # 删除品牌对应的图片
    image_name = trademark_info["logoUrl"].split("/")[-1]
    os.remove(f"{TRADEMARK_PATH}/{image_name}")

    return success(None)