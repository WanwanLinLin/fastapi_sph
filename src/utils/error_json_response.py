# -*- coding：utf-8 -*-
from fastapi import HTTPException


def customize_error_response(code: int, error_message: str):
    raise HTTPException(status_code=code,
                        detail={
                            "code": code,
                            "message": error_message,
                            "data": None,
                            "ok": False
                        })


if __name__ == '__main__':
    from fastapi import status

    customize_error_response(status.HTTP_400_BAD_REQUEST, "你错啦")
