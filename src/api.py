# -*- coding：utf-8 -*-
import json
import requests
import uvicorn
from fastapi import FastAPI, status
# from modules import users_router
from db import Base, engine
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from modules import users_router, ValidateList

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router)

# 商品微服务
GOODS_SERVICE_URL = "http://127.0.0.1:6666"


# 重写HTTPException处理程序
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # return PlainTextResponse(json.dumps(exc.detail), status_code=exc.status_code)
    return JSONResponse(exc.detail, status_code=exc.status_code)


@app.get("/")
async def main():
    return {"message": "There will be a fastapi project"}


# ### 构建商品微服务
# 返回所有类别列表数据(三级联动)的接口
@app.get("/v1/goods/getBaseCategoryList", responses={
    status.HTTP_200_OK: {"description": "Success"}})
async def get_base_category_list():
    result = requests.post(url=f"{GOODS_SERVICE_URL}/getBaseCategoryList")

    return result.json()


# 展示商品列表的接口
@app.post("/v1/goods/list", responses={
    status.HTTP_200_OK: {"description": "Success"}})
async def display_goods_list(goods_info: ValidateList):
    data = {
        "category1Id": goods_info.category1Id,
        "category2Id": goods_info.category2Id,
        "category3Id": goods_info.category3Id,
        "categoryName": goods_info.categoryName,
        "keyword": goods_info.keyword,
        "props": goods_info.props,
        "trademark": goods_info.trademark,
        "order": goods_info.order,
        "pageNo": goods_info.pageNo,
        "pageSize": goods_info.pageSize
    }
    print(data)

    result = requests.post(url=f"{GOODS_SERVICE_URL}/list",
                           json=data)

    return result.json()


# 展示商品详情的接口
@app.get("/v1/goods/item/{sku_id}", responses={
    status.HTTP_200_OK: {"description": "Success"}})
async def show_goods_detail(sku_id: int):
    result = requests.get(url=f"{GOODS_SERVICE_URL}/item/{sku_id}")

    return result.json()

if __name__ == '__main__':
    uvicorn.run(app)