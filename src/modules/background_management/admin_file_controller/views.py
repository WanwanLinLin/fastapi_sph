# -*- coding：utf-8 -*-
import os

from . import schemas
from db import SessionLocal
from utils import TRADEMARK_PATH, CATEGORY_PATH
from fastapi import APIRouter, Depends, status, HTTPException, Header, UploadFile
from utils import success, customize_error_response, create_numbering, DoubleTokenAccess

session = SessionLocal()
router = APIRouter(
    prefix="/v1/admin/fileController",
    tags=["manage upload file module"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# 上传品牌图片的接口
@router.post("/fileUpload", responses={
    status.HTTP_200_OK: {"description": "Success"}
}, dependencies=[Depends(DoubleTokenAccess.val_refresh_token),
                 Depends(DoubleTokenAccess.val_access_token)])
async def upload_file_by_user(file_: UploadFile):
    path_to_save_database = f"http://127.0.0.1:8000/static/trademark/{file_.filename}"
    real_file_path = os.path.join(TRADEMARK_PATH, file_.filename)
    if os.path.exists(real_file_path):
        customize_error_response(code=400,
                                 error_message="Storage failed! The file already exists!")

    # 保存上传的文件
    file_content = file_.file.read()
    with open(real_file_path, 'wb') as f:
        f.write(file_content)

    return success(path_to_save_database)