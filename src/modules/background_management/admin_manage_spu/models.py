# -*- coding：utf-8 -*-
from nosql_db import client

# 获取SPU基础属性
Goods_se_sale_attrs = client.goods.Goods_se_sale_attrs

# 获取SPU的图片
Goods_se_image_list = client.goods.Goods_se_image_list

"""
存放sku信息的数据库
    注意：一个SPU可能会有多个SKU实例
"""
Goods_se_details_sku = client.goods.Goods_se_details_sku

# 某个商品的详细信息的集合SPU
Goods_se_details = client.goods.Goods_se_details
