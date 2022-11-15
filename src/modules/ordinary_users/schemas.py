# -*- coding：utf-8 -*-
from typing import List, Union

from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    username: str = Field(max_length=15, min_length=3)
    password: str = Field(max_length=30, min_length=3)

    class Config:
        orm_mode = True
