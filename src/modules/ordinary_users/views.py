# -*- coding：utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status
from . import schemas
from .models import User
from utils import verify_password

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

    return {
        "username": info.username,
        "x-token": info.password,
    }
