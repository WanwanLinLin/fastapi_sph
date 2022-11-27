# -*- coding：utf-8 -*-
import re

from typing import Optional
from pydantic import BaseModel, validator


class SubmitOrder(BaseModel):
    consignee: str
    consigneeTel: str
    deliveryAddress: str
    paymentWay: str
    orderComment: str
    orderDetailList: list
