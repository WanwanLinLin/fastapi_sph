# -*- coding: utf-8 -*-
from .models import Goods_trademark
from typing import List, Optional
from utils import customize_error_response
from pydantic import BaseModel, ValidationError, validator


class SaveTrademark(BaseModel):
    tmName: str
    logoUrl: str

    # 验证品牌名是否重复
    @validator("tmName")
    def val_tm_name(cls, v):
        info = Goods_trademark.find_one({"tmName": v})
        if info:
            customize_error_response(code=201,
                                     error_message="Sorry, the brand name cannot be repeated!")
        return v


class UpdateTrademark(BaseModel):
    id: int
    tmName: str
    logoUrl: str
