# -*- coding：utf-8 -*-
from fastapi import APIRouter, Depends, status, HTTPException
from db import FirstCategory, SessionLocal
from utils import success


session = SessionLocal()

router = APIRouter(
    prefix="/v1/goods",
    tags=["manage goods module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# 返回所有类别列表数据(三级联动)的接口
@router.get('/getBaseCategoryList', responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def get_base_category_list():
    data: list = []
    dict_: dict = {}
    all_first_category = session.query(FirstCategory).all()
    for every_first_category in all_first_category:
        dict_.update({"categoryName": every_first_category.category_name,
                      "categoryId": every_first_category.id,
                      "categoryChild": []})
        for i, every_second_category in enumerate(every_first_category.owner):
            dict_["categoryChild"].append({"categoryName": every_second_category.category_name,
                                           "categoryId": every_second_category.id,
                                           "categoryChild": []})
            for every_third_category in every_second_category.owner:
                dict_["categoryChild"][i]["categoryChild"].append({"categoryName": every_third_category.category_name,
                                                                   "categoryId": every_third_category.id,
                                                                   })
        data.append(dict_)
        dict_ = {}

    return success(data)
