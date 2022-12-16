# -*- coding：utf-8 -*-
from . import schemas
from .models import Goods_se_attrs
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Header
from db import FirstCategory, SecondCategory, ThirdCategory, SessionLocal
from utils import success, customize_error_response, create_numbering, DoubleTokenAccess

session = SessionLocal()
router = APIRouter(
    prefix="/v1/admin/categoryManagement",
    tags=["manage category module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# 获取商品一级分类的接口
@router.get("/getCategory1", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_category1_by_admin():
    get_category1_list: list = []
    category1_info: List[FirstCategory] = session.query(FirstCategory).all()

    # 构造前端需要的响应格式
    for each_category1 in category1_info:
        get_category1_list.append({
            "id": each_category1.id,
            "name": each_category1.category_name
        })

    return success(get_category1_list)


# 获取商品二级分类的接口
@router.get("/getCategory2/{category1_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_category2_by_admin(category1_id: int):
    category2_list: list = []
    category2_info: List[SecondCategory] = session.query(SecondCategory).filter(SecondCategory.owner_id == category1_id).all()

    # 构造前端需要的响应格式
    for each_category2 in category2_info:
        category2_list.append({
            "id": each_category2.id,
            "name": each_category2.category_name
        })
    return success(category2_list)


# 获取商品三级分类的接口
@router.get("/getCategory3/{category2_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_category2_by_admin(category2_id: int):
    category3_list: list = []
    category3_info: List[ThirdCategory] = session.query(ThirdCategory).filter(ThirdCategory.owner_id == category2_id).all()

    # 构造前端需要的响应格式
    for each_category3 in category3_info:
        category3_list.append({
            "id": each_category3.id,
            "name": each_category3.category_name
        })

    return success(category3_list)


# 获取商品属性的接口
@router.get("/attrInfoList/{category1_id}/{category2_id}/{category3_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def get_attr_info_list(category1_id: int, category2_id: int, category3_id: int):
    # data为响应数据
    data: list = []
    category3_id = str(category3_id)
    attr_list = list(Goods_se_attrs.find({"connect_category3Id": category3_id}, {"_id": 0}))

    for i, attr_ in enumerate(attr_list, start=1):
        attr_value_list = []
        for j, value_ in enumerate(attr_["attrValueList"], start=1):
            attr_value_list.append({
                "id": j,
                "valueName": value_,
                "attrId": attr_["attrId"]
            })

        data.append({
            "id": attr_["id"],
            "attrName": attr_["attrName"],
            "categoryId": category3_id,
            "categoryLevel": 3,
            "attrValueList": attr_value_list
        })

    return success(data)


# 添加属性或者修改商品属性的接口
@router.post("/saveAttrInfo", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def save_or_update_attr_info(attr_info: schemas.SaveAttrInfo):
    attr_id_list: list = []
    attr_value_list: list = []

    for attr_ in attr_info.attrValueList:
        if len(attr_) == 2:
            attr_id_list.append(attr_["attrId"])
            attr_value_list.append(attr_["valueName"])
        else:
            attr_value_list.append(attr_["valueName"])

    # 判断是更新属性还是添加属性
    if not attr_id_list:
        # 此时为增加新属性的操作
        # 首先创建一个自增长的id
        id_list = list(Goods_se_attrs.find().sort("id", -1))
        if not id_list:
            id_ = 1
        else:
            id_ = id_list[0]["id"] + 1
        # 再创建一个自增长的attrId
        attr_id_list = list(Goods_se_attrs.find().sort("attrId", -1))
        if not attr_id_list:
            attr_id = 1
        else:
            attr_id = attr_id_list[0]["attrId"] + 1
        # 处理属性值和属性id，然后将它们插入数据库中
        Goods_se_attrs.insert_one({
            "attrId": attr_id,
            "attrValueList": attr_value_list,
            "attrName": attr_info.attrName,
            "id": id_,
            "connect_category3Id": str(attr_info.categoryId),
            "category_level": str(attr_info.categoryLevel)
        })
        return success(None)

    # 此时为修改原有属性的操作
    Goods_se_attrs.update_one({"attrId": attr_id_list[0]},
                              {"$set": {
                                  "attrName": attr_info.attrName,
                                  "attrValueList": attr_value_list,
                              }})
    return success(None)


# 删除属性的接口
@router.get("/deleteAttr/{attr_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def delete_attr(attr_id: int):
    Goods_se_attrs.delete_one({"attrId": attr_id})

    return success(None)