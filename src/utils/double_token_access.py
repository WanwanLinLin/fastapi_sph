# -*- coding：utf-8 -*-
import os
import binascii
from typing import Union
from nosql_db import r_5
from fastapi import status, HTTPException, Depends, Header


class DoubleTokenAccess:
    """
    目前方案是：可以跟前端约定一个状态码，如果前端
    捕获到这个状态码则重置access_token
    (https://juejin.cn/post/7035280102636126244)
    """

    def __init__(self):
        pass

    @staticmethod
    def create_numbering(length=24):
        s = binascii.b2a_base64(os.urandom(length))[:-1].decode('utf-8')
        for x in ['+', '=', '/', '?', '&', '%', "#"]:
            s = s.replace(x, "")
        return s

    @classmethod
    async def val_access_token(cls, access_token: str = Header()):
        get_admin_username_by_access_token = r_5.get(access_token)
        if get_admin_username_by_access_token:
            return get_admin_username_by_access_token
        else:
            # # access-token验证不通过,返回指定状态码,提示前端用refresh-token刷新
            raise HTTPException(status_code=409,
                                detail={
                                    "code": 409,
                                    "message": "The access-token verification fails!",
                                    "data": None,
                                    "ok": False
                                })

    @classmethod
    async def val_refresh_token(cls, refresh_token: Union[str, None] = Header(default=None)):
        """

        :param refresh_token: 专门用于刷新access-token
        :return:
        """
        if not refresh_token:
            return
        get_admin_username_by_refresh_token = r_5.get(refresh_token)
        if get_admin_username_by_refresh_token:
            # refresh-token有效，重置access-token
            await cls.reset_access_token(refresh_token=refresh_token)
        else:
            raise HTTPException(status_code=400,
                                detail={
                                    "code": 400,
                                    "message": "Token expired, please login again!",
                                    "data": None,
                                    "ok": False
                                })

    @classmethod
    async def reset_access_token(cls, refresh_token: str = Header()):
        get_admin_username_by_refresh_token = r_5.get(refresh_token)
        if get_admin_username_by_refresh_token:
            # refresh_token验证通过，刷新access_token
            access_token = f'access-{get_admin_username_by_refresh_token}-{cls.create_numbering(length=40)}'
            r_5.setex(access_token, 60 * 60 * 2, get_admin_username_by_refresh_token)
            data = {
                "username": get_admin_username_by_refresh_token,
                "access_token": access_token,
                "refresh_token": refresh_token
            }

            raise HTTPException(status_code=201,
                                detail={
                                    "code": 410,
                                    "message": "Reset access-token!",
                                    "data": data,
                                    "ok": False
                                })
        else:
            raise HTTPException(status_code=400,
                                detail={
                                    "code": 400,
                                    "message": "Token expired, please login again!",
                                    "data": None,
                                    "ok": False
                                })

    @classmethod
    async def delete_double_token(cls, admin_name: str):
        admin_token_list = r_5.keys(pattern=f'*-{admin_name}-*')
        for i in admin_token_list:
            r_5.delete(i)


if __name__ == '__main__':
    pass
