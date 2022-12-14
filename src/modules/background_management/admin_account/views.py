# -*- coding：utf-8 -*-
from . import schemas
from nosql_db import r_5
from db import SessionLocal, AdminUser
from utils import success, customize_error_response, create_numbering, DoubleTokenAccess
from fastapi import APIRouter, Depends, status, HTTPException

session = SessionLocal()
router = APIRouter(
    prefix="/v1/admin",
    tags=["manage admin module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# 后台管理员登录的接口
@router.post("/acl/index/login", responses={
    status.HTTP_200_OK: {"description": "Success"}
})
async def admin_user_login(login_info: schemas.ValAdminLogin):
    admin_name = login_info.username
    hash_password = login_info.encrypt_password
    # 验证用户名和密码
    try:
        admin_info: AdminUser = session.query(AdminUser).filter(AdminUser.username == admin_name).first()
        assert admin_info.check_password(hash_password)
    except Exception:
        customize_error_response(code=203,
                                 error_message="Sorry, the account or password is wrong!")

    # 若登录成功，则为管理员签发双token
    access_token = f'access-{admin_name}-{create_numbering(length=40)}'
    refresh_token = f'refresh-{admin_name}-{create_numbering(length=40)}'
    r_5.setex(access_token, 60 * 60 * 2, admin_name)
    r_5.setex(refresh_token, 60 * 60 * 24 * 7, admin_name)

    data = {
        "username": admin_name,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

    return success(data)


# 获取后台管理系统人员信息的接口
@router.get("/acl/index/info", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token)])
async def get_admin_info(admin_name: str = Depends(DoubleTokenAccess.val_access_token)):
    data = {"name": admin_name}
    return success(data)