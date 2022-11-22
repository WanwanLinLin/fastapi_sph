# -*- coding：utf-8 -*-
import math
from . import schemas
from utils import success
from db import FirstCategory, SessionLocal
from fastapi import APIRouter, Depends, status, HTTPException
from .models import Goods, Goods_se_attrs, Goods_se_details_sku, Goods_se_details
from utils import customize_error_response

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


# 展示商品列表的接口
@router.post('/list', responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def display_goods_list(get_list_info: schemas.ValidateList):
    # 定义品牌总列表
    trademark_list: list = []
    # 定义商品属性总列表
    attrs_list: list = []
    # 定义货物总列表
    goods_list: list = []

    # 第一种情况：设置默认页面
    if not get_list_info.category1Id and not get_list_info.category2Id and not get_list_info.category3Id and \
            not get_list_info.categoryName and not get_list_info.keyword and not \
            get_list_info.props and not get_list_info.trademark:
        all_info = list(Goods_se_details_sku.find({"tmId": 1}, {"_id": 0}))
        attrs_info = list(Goods_se_attrs.find({"connect_category3Id": "4"}, {"_id": 0}))
        for x in all_info:
            trademark_list.append({"tmId": x["tmId"], "tmName": x["tmName"]})
        # 获取不重复的品牌数据
        trademark_list = [dict(t) for t in set([tuple(d.items()) for d in trademark_list])]

        for x_ in all_info:
            goods_list.append(x_)

        for y in attrs_info:
            attrs_list.append(y)

        # 判断商品的状态是上架还是下架
        is_sale_or_cancel_sale = []
        for x_ in goods_list:
            if x_["isSale"] == 1:
                is_sale_or_cancel_sale.append(x_)
        goods_list = is_sale_or_cancel_sale
        total = len(goods_list)

        # 首页默认分页效果
        page_no = int(get_list_info.pageNo)
        page_size = int(get_list_info.pageSize)
        limit_start = (page_no - 1) * page_size
        page_total = math.ceil(total / page_size)
        goods_list = goods_list[limit_start:page_no * page_size]

        # 处理order参数
        if get_list_info.order == "1:asc":
            goods_list = sorted(goods_list, key=lambda goods_list: goods_list["spuId"])
        elif get_list_info.order == "1:desc":
            goods_list = sorted(goods_list, key=lambda goods_list: goods_list["spuId"], reverse=True)
        elif get_list_info.order == "2:asc":
            goods_list = sorted(goods_list, key=lambda goods_list: goods_list["price"])
        else:
            goods_list = sorted(goods_list, key=lambda goods_list: goods_list["price"], reverse=True)

        data = {
            "trademarkList": trademark_list,
            "attrsList": attrs_list,
            "goodsList": goods_list,
            "total": total,
            "pageSize": page_size,
            "pageNo": page_no,
            "totalPages": page_total
        }

        return success(data)

    # 第二种情况，前端传递来了参数（默认参数除外）
    page_no = int(get_list_info.pageNo)
    page_size = int(get_list_info.pageSize)
    # 该变量用于表示跳过前面多少条
    limit_start = (page_no - 1) * page_size

    # 处理 trademark 的值
    if get_list_info.trademark:
        trademark = get_list_info.trademark.split(":")
        all_info_2 = list(Goods_se_details_sku.find({"tmId": int(trademark[0])},
                                                    {"_id": 0}))

    # 处理由三级类目列表进行搜索的结果
    elif get_list_info.category1Id:
        all_info_2 = list(Goods_se_details_sku.find({"category1Id": get_list_info.category1Id},
                                                    {"_id": 0}))

    elif get_list_info.category2Id:
        all_info_2 = list(Goods_se_details_sku.find({"category2Id": get_list_info.category2Id},
                                                    {"_id": 0}))
    else:
        all_info_2 = list(Goods_se_details_sku.find({"category3Id": get_list_info.category3Id},
                                                    {"_id": 0}))

    if all_info_2 and get_list_info.keyword:
        # 这是对应同时使用三级类目导航和keyword导航的情况的情况
        for x in all_info_2:
            if get_list_info.keyword in x["skuName"]:
                trademark_list.append({"tmId": x["tmId"], "tmName": x["tmName"]})

        for x_ in all_info_2:
            if get_list_info.keyword in x_["tmName"]:
                attrs_list = list(Goods_se_attrs.find({"connect_category3Id": x_["category3Id"]},
                                                      {"_id": 0}))
                goods_list.append(x_)

    elif all_info_2:
        # 这是对应只有三级类目导航的情况
        for x in all_info_2:
            trademark_list.append({"tmId": x["tmId"], "tmName": x["tmName"]})

        for x_ in all_info_2:
            attrs_list = list(Goods_se_attrs.find({"connect_category3Id": x_["category3Id"]},
                                                  {"_id": 0}))
            goods_list.append(x_)

    elif get_list_info.keyword:
        # 这是对应只有 keyword 的情况
        all_info_3 = list(Goods_se_details_sku.find({}, {"_id": 0}))
        for x in all_info_3:
            if get_list_info.keyword in x["tmName"] or get_list_info.keyword in x["skuName"]:
                trademark_list.append({"tmId": x["tmId"], "tmName": x["tmName"]})

        for x_ in all_info_3:
            if get_list_info.keyword in x_["tmName"] or get_list_info.keyword in x_["skuName"]:
                attrs_list = list(Goods_se_attrs.find({"connect_category3Id": x_["category3Id"]},
                                                      {"_id": 0}))
                goods_list.append(x_)

    else:
        pass

    # 处理props参数
    if get_list_info.props:
        props_list = []
        for x in get_list_info.props:
            x = x.split(":")
            for z in goods_list:
                for z_ in z["skuAttrValueList"]:
                    if x[0] == z_["attrId"] and x[1] == z_["valueName"]:
                        if z not in props_list:
                            props_list.append(z)
        goods_list = props_list

    # 判断商品的状态是上架还是下架
    is_sale_or_cancel_sale = []
    for x_ in goods_list:
        if x_["isSale"] == 1:
            is_sale_or_cancel_sale.append(x_)
    goods_list = is_sale_or_cancel_sale

    total = len(goods_list)
    # 采用切片方式方便分页
    goods_list = goods_list[limit_start:page_no * page_size]

    # 获取不重复的品牌数据
    trademark_list = [dict(t) for t in set([tuple(d.items()) for d in trademark_list])]

    # 获取分页总数
    page_total = math.ceil(total / page_size)

    # 处理order参数
    if get_list_info.order == "1:asc":
        goods_list = sorted(goods_list, key=lambda goods_list: goods_list["spuId"])
    elif get_list_info.order == "1:desc":
        goods_list = sorted(goods_list, key=lambda goods_list: goods_list["spuId"], reverse=True)
    elif get_list_info.order == "2:asc":
        goods_list = sorted(goods_list, key=lambda goods_list: goods_list["price"])
    else:
        goods_list = sorted(goods_list, key=lambda goods_list: goods_list["price"], reverse=True)

    data = {
        "trademarkList": trademark_list,
        "attrsList": attrs_list,
        "goodsList": goods_list,
        "total": total,
        "pageSize": page_size,
        "pageNo": page_no,
        "totalPages": page_total
    }

    return success(data)


# 展示商品详情的接口
@router.get('/item/{sku_id}', responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def show_goods_detail(sku_id: int):
    try:
        sku_info = Goods_se_details_sku.find_one({"id": sku_id}, {"_id": 0})
        spu_id = sku_info["spuId"]
        item_info = Goods_se_details.find_one({"spuId": spu_id}, {"_id": 0})
        item_info["skuInfo"] = sku_info
    except Exception as e:
        customize_error_response(code=404, error_message="Sorry, the product details page does not exist!")

    return success(item_info)
