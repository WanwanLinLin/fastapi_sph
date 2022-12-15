# -*- coding：utf-8 -*-
from . import schemas
from .models import Goods_se_attrs
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
}, dependencies=[Depends(DoubleTokenAccess.val_access_token),
                 Depends(DoubleTokenAccess.val_refresh_token)])
async def get_category1_by_admin():
    get_category1_list: list = []
    category1_info: list = session.query(FirstCategory).all()

    # 构造前端需要的响应格式
    for each_category1 in category1_info:
        get_category1_list.append({
            "id": each_category1.id,
            "name": each_category1.category_name
        })

    return success(get_category1_list)