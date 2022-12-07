# -*- coding：utf-8 -*-
# from .ordinary_users import router as users_router
# from .goods_manage import router as manage_goods_router
from .ordinary_users import UserLogin, UserRegister, ValidatePhone, ValidateEditPassword
from .goods_manage import ValidateList
from .trade_manage import SubmitOrder
