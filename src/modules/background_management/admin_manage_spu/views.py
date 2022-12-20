# -*- coding：utf-8 -*-
import os
import time
import math

from . import schemas
from .models import *
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Header
from db import FirstCategory, SecondCategory, ThirdCategory, SessionLocal
from utils import success, customize_error_response, create_numbering, DoubleTokenAccess, CATEGORY_PATH

session = SessionLocal()
router = APIRouter(
    prefix="/v1/admin/spuManagement",
    tags=["manage SKU module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# 获取SPU列表的接口
@router.get("/product/{page}/{limit}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_spu_list(page: int, limit: int, category3_id: int):
    category3_id = str(category3_id)
    spu_info = list(Goods_se_details.find({"category3Id": category3_id}, {"_id": 0}))
    records: List[dict] = []
    for spu_ in spu_info:
        records.append({
            "id": spu_["spuId"],
            "spuName": spu_["spuName"],
            "description": spu_["description"],
            "category3Id": spu_["category3Id"],
            "tmId": spu_["tmId"],
            "spuSaleAttrList": None,
            "spuImageList": None
        })

    # 实现简单的分页功能
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


# 获取SPU基础属性的接口
@router.get("/product/baseSaleAttrList", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_base_sale_attr_list():
    sale_attr_list = list(Goods_se_sale_attrs.find({}, {"_id": 0}))

    return success(sale_attr_list)


# 获取SPU基本信息的接口
@router.get("/product/getSpuById/{spu_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_spu_by_id(spu_id: int):
    spu_info = Goods_se_details.find_one({"spuId": spu_id}, {"_id": 0})
    if not spu_info:
        customize_error_response(code=201,
                                 error_message="Sorry, the spu information does not exist!")

    data = {
        "id": spu_info["spuId"],
        "spuName": spu_info["spuName"],
        "description": spu_info["description"],
        "category3Id": spu_info["category3Id"],
        "tmId": spu_info["tmId"],
        "spuSaleAttrList": spu_info["spuSaleAttrList"]
    }

    return success(data)


# 获取SPU图片的接口
@router.get("/product/spuImageList/{spu_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_spu_image_list(spu_id: int):
    spu_image_list = list(Goods_se_image_list.find({"spuId": spu_id}, {"_id": 0}))

    return success(spu_image_list)


# 修改SPU信息的接口
@router.post("/product/updateSpuInfo", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def update_spu_info(spu_info: schemas.UpdateOrSaveSpuInfo):
    # 处理spuSaleAttrList
    new_spu_sale_attr_list: List[dict] = []
    for i, x_ in enumerate(spu_info.spuSaleAttrList, start=1):
        dict_ = {
            "id": i,
            'baseSaleAttrId': int(x_['baseSaleAttrId']),
            'saleAttrName': x_['saleAttrName'],
            "spuId": spu_info.id
        }
        new_x = []
        for j, y_ in enumerate(x_['spuSaleAttrValueList'], start=1):
            dict_2 = {
                "id": j,
                'baseSaleAttrId': y_['baseSaleAttrId'],
                "saleAttrName": x_['saleAttrName'],
                'saleAttrValueName': y_['saleAttrValueName'],
                "spuId": spu_info.id,
                "isChecked": "0"
            }
            new_x.append(dict_2)
        dict_["spuSaleAttrValueList"] = new_x
        new_spu_sale_attr_list.append(dict_)
    # print(new_spu_sale_attr_list)

    # 处理spuImageList
    # 这里采用先全部删除再重新插入的方法
    Goods_se_image_list.delete_many({"spuId": spu_info.id})

    id_list = list(Goods_se_image_list.find().sort("id", -1))
    if not id_list:
        id = 1
    else:
        id = id_list[0]["id"] + 1

    for i, x_ in enumerate(spu_info.spuImageList, start=int(id)):
        Goods_se_image_list.insert_one({
            "id": i,
            "spuId": spu_info.id,
            "imgName": x_["imageName"],
            "imgUrl": x_["imageUrl"]
        })

    # 最后更新Goods_se_details数据库
    # 更新description和spuName
    Goods_se_details.update_one({"spuId": spu_info.id},
                                {"$set": {"spuSaleAttrList": new_spu_sale_attr_list,
                                          "spuName": spu_info.spuName, "description": spu_info.description}})

    return success(None)


# 添加SPU信息的接口
@router.post("/product/saveSpuInfo", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def save_spu_info(spu_info: schemas.UpdateOrSaveSpuInfo):
    # 1.创建一个新的Goods_se的ID，与SPU_ID并用
    goods_se_spu_id_list = list(Goods_se_details.find().sort("spuId", -1))
    if not goods_se_spu_id_list:
        goods_se_spu_id = 1
    else:
        goods_se_spu_id = goods_se_spu_id_list[0]["spuId"] + 1.0

    # 2.处理spuSaleAttrList
    new_spu_sale_attr_list = []
    for i, x_ in enumerate(spu_info.spuSaleAttrList, start=1):
        dict_ = {
            "id": i,
            'baseSaleAttrId': int(x_['baseSaleAttrId']),
            'saleAttrName': x_['saleAttrName'],
            "spuId": goods_se_spu_id
        }
        new_x = []
        for j, y_ in enumerate(x_['spuSaleAttrValueList'], start=1):
            dict_2 = {
                "id": j,
                'baseSaleAttrId': y_['baseSaleAttrId'],
                "saleAttrName": x_['saleAttrName'],
                'saleAttrValueName': y_['saleAttrValueName'],
                "spuId": goods_se_spu_id,
                "isChecked": "0"
            }
            new_x.append(dict_2)
        dict_["spuSaleAttrValueList"] = new_x
        new_spu_sale_attr_list.append(dict_)

    # 3.处理spuImageList
    image_id_list = list(Goods_se_image_list.find().sort("id", -1))
    if not image_id_list:
        id = 1
    else:
        id = image_id_list[0]["id"] + 1

    for i, x_ in enumerate(spu_info.spuImageList, start=int(id)):
        Goods_se_image_list.insert_one({
            "id": i,
            "spuId": goods_se_spu_id,
            "imgName": x_["imageName"],
            "imgUrl": x_["imageUrl"]
        })

    # 4.增加一条Goods_se_details记录
    Goods_se_details.insert_one({
        "spuId": goods_se_spu_id,
        "spuSaleAttrList": new_spu_sale_attr_list,
        "skuInfo": {},
        "categoryView": {},
        "valuesSkuJson": "",
        "category3Id": str(spu_info.category3Id),
        "description": spu_info.description,
        "spuName": spu_info.spuName,
        "tmId": spu_info.tmId
    })

    return success(None)


# 删除相应SPU信息的接口
@router.delete("/product/deleteSpu/{spu_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def delete_spu_by_id(spu_id: int):
    # 删除Goods_details中的信息
    Goods_se_details.delete_one({"spuId": spu_id})
    # 删除Goods_se_image_list中的信息
    # 删除SPU对应的图片
    image_name_list = list(Goods_se_image_list.find({"spuId": spu_id}, {"_id": 0}))
    for x_ in image_name_list:
        image_name = x_["imgUrl"].split("/")[-1]
        os.remove(f"{CATEGORY_PATH}/{image_name}")

    Goods_se_image_list.delete_many({"spuId": spu_id})

    return success(None)




