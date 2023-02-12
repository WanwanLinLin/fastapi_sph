# -*- coding：utf-8 -*-
# from .ordinary_users import router as users_router
# from .goods_manage import router as manage_goods_router
from .ordinary_users import UserLogin, UserRegister, ValidatePhone, ValidateEditPassword
from .goods_manage import ValidateList
from .trade_manage import SubmitOrder
from .time_limited_seckill import SubmitSecKillOrder

# 后台管理模块
from .background_management import (admin_user_router, admin_manage_category_router,
                                    admin_file_manage_router, admin_manage_sku_router,
                                    admin_manage_spu_router, admin_manage_trademark_router)
