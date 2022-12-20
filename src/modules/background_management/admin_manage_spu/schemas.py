# -*- coding：utf-8 -*-
from typing import Optional, List
from pydantic import BaseModel


class UpdateOrSaveSpuInfo(BaseModel):
    category3Id: str
    description: str
    id: Optional[int]
    spuName: str
    spuSaleAttrList: List[dict]
    tmId: int
    spuImageList: List[dict]