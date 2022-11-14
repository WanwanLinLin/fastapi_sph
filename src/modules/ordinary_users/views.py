# -*- coding：utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from . import schemas
from .models import User

router = APIRouter(
    prefix="/v1/users",
    tags=["users module"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", responses={
    200: {"description": "Success"}
})
async def login(info: schemas.UserLogin):
    user = User.find_one({"username": info.username, "password": info.password})
    if not user:
        raise HTTPException(status_code=404, detail="Users not found")
    return {
        "username": info.username,
        "x-token": info.password,
    }
