# -*- coding：utf-8 -*-
import time
import math

from . import schemas
from .models import *
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Header
from db import FirstCategory, SecondCategory, ThirdCategory, SessionLocal
from utils import success, customize_error_response, create_numbering, DoubleTokenAccess

session = SessionLocal()
router = APIRouter(
    prefix="/v1/admin/skuManagement",
    tags=["manage SKU module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# 获取某个SPU全部图片的接口
@router.get("/product/spuImageList/{spu_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_all_spu_images(spu_id: int):
    data: List[dict] = []
    all_spu_image_list = list(Goods_se_image_list.find({"spuId": spu_id}, {"_id": 0}))
    for i, every_image in enumerate(all_spu_image_list, start=1):
        data.append({
            "id": i,
            "spuId": spu_id,
            "imgName": every_image["imgName"],
            "imgUrl": every_image["imgUrl"]
        })

    return success(data)


# 获取某个SPU全部销售属性的接口
@router.get("/product/spuSaleAttrList/{spu_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_spu_sale_attr_list(spu_id: int):
    spu_sale_attr_list = Goods_se_details.find_one({"spuId": spu_id})["spuSaleAttrList"]

    return success(spu_sale_attr_list)


# 保存SKU信息的接口
@router.post("/product/saveSkuInfo", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def save_sku_info(sku_info: schemas.SaveSkuInfo):
    # 1.生成一个新的sku_id
    id_list = list(Goods_se_details_sku.find({}).sort("id", -1))
    if id_list:
        sku_id = id_list[0]["id"] + 1
    else:
        sku_id = 1

    # 2.处理skuImageList
    new_sku_image_list: List[dict] = []
    for i, sku_image_ in enumerate(sku_info.skuImageList, start=1):
        new_sku_image_list.append({
            "id": sku_image_['spuImgId'],
            "skuId": sku_id,
            "imageName": sku_image_['imgName'],
            "imageUrl": sku_image_['imgUrl'],
            "spuImgId": sku_image_['spuImgId'],
            "isDefault": str(sku_image_['isDefault'])
        })

    # 3.处理skuAttrValueList
    new_sku_attr_value_list: List[dict] = []
    for i, sku_attr_ in enumerate(sku_info.skuAttrValueList, start=1):
        new_sku_attr_value_list.append({
            "id": i,
            "attrId": sku_attr_['attrId'],
            "valueId": sku_attr_['valueId'],
            'valueName': sku_attr_['valueName'],
            "skuId": sku_id
        })

    # 4.处理skuSaleAttrValueList
    new_sku_sale_attr_value_list: List[dict] = []
    for i, sku_sale_attr_ in enumerate(sku_info.skuSaleAttrValueList, start=1):
        new_sku_sale_attr_value_list.append({
            "id": i,
            "saleAttrId": sku_sale_attr_['saleAttrId'],
            "saleAttrValueId": sku_sale_attr_['saleAttrValueId']
        })

    # 5.反向查询得出对应的category2Id和category1Id以及查出tmName
    category2_id = session.query(ThirdCategory).filter(ThirdCategory.id == int(sku_info.category3Id)).first().owner_id
    category1_id = session.query(SecondCategory).filter(SecondCategory.id == int(category2_id)).first().owner_id
    tm_name = Goods_trademark.find_one({"id": sku_info.tmId}, {"_id": 0})["tmName"]

    # 6.整合数据
    sku_info = {
        "id": sku_id,
        "spuId": sku_info.spuId,
        "price": sku_info.price,
        "skuName": sku_info.skuName,
        "skuDesc": sku_info.skuDesc,
        "weight": sku_info.weight,
        "createTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        "tmId": sku_info.tmId,
        "tmName": tm_name,
        "category3Id": sku_info.category3Id,
        "category2Id": str(category2_id),
        "category1Id": str(category1_id),
        "skuDefualtImg": sku_info.skuDefaultImg,
        "defualtImg": sku_info.skuDefaultImg,
        "isSale": 1,
        "skuImageList": new_sku_image_list,
        "skuAttrValueList": new_sku_attr_value_list,
        "skuSaleAttrValueList": new_sku_sale_attr_value_list
    }

    # 5.插入数据库
    Goods_se_details_sku.insert_one(sku_info)

    return success(None)


# 查找某个SPU对应的所有SKU的接口
@router.get("/product/findBySpuId/{spu_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def find_sku_by_spu_id(spu_id: int):
    data = list(Goods_se_details_sku.find({"spuId": spu_id},
                                          {"_id": 0, "skuImageList": 0,
                                           "skuAttrValueList": 0, "skuSaleAttrValueList": 0}))
    return success(data)


# 展示所有SKU的接口
@router.get("/product/list/{page}}/{limit}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_sku_list(page: int, limit: int):
    sku_list = list(Goods_se_details_sku.find({},
                                              {"_id": 0, "skuImageList": 0,
                                               "skuAttrValueList": 0, "skuSaleAttrValueList": 0}))
    # 实现简单的分页效果
    # 该变量用于表示跳过前面多少条
    limit_start = (page - 1) * limit
    # 获取品牌总数量
    total = len(sku_list)
    # 获取实际需要展示的条数
    sku_list = sku_list[limit_start:page * limit]
    # 获取分页总数
    pages = int(math.ceil(total / limit))

    data = {
        "records": sku_list,
        "total": total,
        "size": limit,
        "current": page,
        "searchCount": True,
        "pages": pages
    }

    return success(data)


# SKU上架的接口
@router.get("/product/onSale/{sku_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def on_sale(sku_id: int):
    Goods_se_details_sku.update_one({"id": sku_id}, {"$set": {"isSale": 1}})

    return success(None)


# SKU下架的接口
@router.get("/product/cancelSale/{sku_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def cancel_sale(sku_id: int):
    Goods_se_details_sku.update_one({"id": sku_id}, {"$set": {"isSale": 0}})

    return success(None)


# 获取SKU详情的接口
@router.get("/product/getSkuById/{sku_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_sku_by_id(sku_id: int):
    sku_info = Goods_se_details_sku.find_one({"id": sku_id}, {"_id": 0})
    new_sku_attr_value_list: List[dict] = []
    new_sku_sale_attr_value_list: List[dict] = []

    for i, sku_ in enumerate(sku_info["skuAttrValueList"], start=1):
        attr_name = Goods_se_attrs.find_one({"attrId": int(sku_["attrId"])})["attrName"]
        new_sku_attr_value_list.append({
            "id": sku_["id"],
            "attrId": int(sku_["attrId"]),
            "valueId": int(sku_["valueId"]),
            "skuId": sku_["skuId"],
            "attrName": attr_name,
            "valueName": sku_["valueName"]
        })

    for i, x_ in enumerate(sku_info["skuSaleAttrValueList"], start=1):
        spu_info = Goods_se_details.find_one({"spuId": sku_info["spuId"]})
        for y_ in spu_info["spuSaleAttrList"]:
            if x_["saleAttrId"] == str(y_["id"]):
                sku_sale_attr_name = y_["saleAttrName"]
                for z_ in y_["spuSaleAttrValueList"]:
                    if x_["saleAttrValueId"] == str(z_["id"]):
                        sku_sale_attr_value_name = z_["saleAttrValueName"]
                        new_sku_sale_attr_value_list.append({
                            "id": x_["id"],
                            "skuId": sku_id,
                            "spuId": sku_info["spuId"],
                            "saleAttrValueId": int(x_["saleAttrValueId"]),
                            "saleAttrId": int(x_["saleAttrId"]),
                            "saleAttrName": sku_sale_attr_name,
                            "saleAttrValueName": sku_sale_attr_value_name
                        })

    # 整合数据
    data = {
        "id": sku_info["id"],
        "spuId": sku_info["spuId"],
        "price": float(sku_info["price"]),
        "skuName": sku_info["skuName"],
        "skuDesc": sku_info["skuDesc"],
        "weight": sku_info["weight"],
        "tmId": sku_info["tmId"],
        "category3Id": int(sku_info["category3Id"]),
        "skuDefaultImg": sku_info["defualtImg"],
        "isSale": sku_info["isSale"],
        "createTime": sku_info["createTime"],
        "skuImageList": sku_info["skuImageList"],
        "skuAttrValueList": new_sku_attr_value_list,
        "skuSaleAttrValueList": new_sku_sale_attr_value_list
    }

    return success(data)