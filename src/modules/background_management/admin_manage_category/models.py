# -*- coding：utf-8 -*-
from nosql_db import client

# 订单集合
Goods = client.goods.Goods

# 商品分类详情集合
Goods_se = client.goods.Goods_se

# 某个商品的属性集合
Goods_se_attrs = client.goods.Goods_se_attrs

# 某个商品的详细信息的集合SPU
Goods_se_details = client.goods.Goods_se_details

# 某个商品的详细信息的集合SKU
Goods_se_details_sku = client.goods.Goods_se_details_sku