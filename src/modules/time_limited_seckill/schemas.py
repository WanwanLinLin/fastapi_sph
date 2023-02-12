# encoding:utf-8
import re

from typing import Optional
from pydantic import BaseModel, validator


class SubmitSecKillOrder(BaseModel):
    id: int = 0
    goods_name: str
    seckill_price: int
