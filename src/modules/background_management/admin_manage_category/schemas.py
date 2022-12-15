# -*- coding：utf-8 -*-
from typing import List
from pydantic import BaseModel


class SaveAttrInfo(BaseModel):
    attrValueList: List[dict]
    categoryId: str
    categoryLevel: int
    attrName: str
