# -*- coding：utf-8 -*-
from nosql_db import client


"""
存放sku信息的数据库
    注意：一个SPU可能会有多个SKU实例
"""
Goods_se_details_sku = client.goods.Goods_se_details_sku

# 获取SPU的图片
Goods_se_image_list = client.goods.Goods_se_image_list

# 某个商品的属性集合
Goods_se_attrs = client.goods.Goods_se_attrs

# 某个商品的详细信息的集合SPU
Goods_se_details = client.goods.Goods_se_details

# 品牌列表的集合
Goods_trademark = client.goods.Goods_trademark