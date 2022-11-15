# -*- coding：utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status
from . import schemas
from .models import User
from nosql_db import r
from utils import verify_password, create_access_token, verify_jwt_access

router = APIRouter(
    prefix="/v1/users",
    tags=["users module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/login", responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def login(info: schemas.UserLogin):
    verify_password(info.password, User, info.username)
    # 生成一个JWT并存到redis中
    jwt_access = create_access_token(info.username, info.password)
    r.setex(info.username, 2 * 60 * 60, jwt_access)
    return {
        "username": info.username,
        "x-token": jwt_access,
    }


@router.get("/testjwt", dependencies=[Depends(verify_jwt_access)])
async def mimi(username: str = Depends(verify_jwt_access)):

    return {"message": "token access!",
            "username": username}