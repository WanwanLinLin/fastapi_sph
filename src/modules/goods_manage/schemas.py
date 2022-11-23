# -*- coding：utf-8 -*-
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from fastapi import status
from utils import customize_error_response
from db import FirstCategory, SecondCategory, ThirdCategory, SessionLocal

session = SessionLocal()


class ValidateList(BaseModel):
    category1Id: Union[str, None] = None
    category2Id: Union[str, None] = None
    category3Id: Union[str, None] = None
    categoryName: Union[str, None] = None
    keyword: Union[str, None] = None
    props: Union[list, None] = None
    trademark: Union[str, None] = None
    order: Union[str, None] = None
    pageNo: Optional[str] = Field(min_length=0)
    pageSize: Optional[str] = Field(min_length=0)

    @validator("category1Id")
    def is_exists(cls, v):
        if not v:
            return
        data = session.query(FirstCategory).filter(FirstCategory.id == int(v)).first()
        if not data:
            customize_error_response(code=status.HTTP_404_NOT_FOUND,
                                     error_message="Sorry, the ID of this first level category does not exist!")
        return v.title()

    @validator("category2Id")
    def is_exists2(cls, v):
        if not v:
            return
        data = session.query(SecondCategory).filter(SecondCategory.id == int(v)).first()
        if not data:
            customize_error_response(code=status.HTTP_404_NOT_FOUND,
                                     error_message="Sorry, the ID of this second level category does not exist!")
        return v.title()

    @validator("category3Id")
    def is_exists3(cls, v):
        # v 为 " " 的情况
        if not v:
            return
        data = session.query(ThirdCategory).filter(ThirdCategory.id == int(v)).first()
        if not data:
            customize_error_response(code=status.HTTP_404_NOT_FOUND,
                                     error_message="Sorry, the ID of this third level category does not exist!")
        return v.title()
