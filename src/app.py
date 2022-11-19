# -*- coding：utf-8 -*-
import json
import uvicorn
from fastapi import FastAPI
# from modules import users_router
from db import Base, engine
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from modules import users_router, manage_goods_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router)
app.include_router(manage_goods_router)


# 重写HTTPException处理程序
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # return PlainTextResponse(json.dumps(exc.detail), status_code=exc.status_code)
    return JSONResponse(exc.detail, status_code=exc.status_code)


@app.get("/")
async def main():
    return {"message": "There will be a fastapi project"}


if __name__ == '__main__':
    uvicorn.run(app)