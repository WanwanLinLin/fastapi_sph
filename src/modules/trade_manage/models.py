# -*- coding: utf-8 -*-
from nosql_db import client

# 订单集合
Orders = client.trade.orders

# 个人作品集合
Portfolios = client.trade.portfolios

# nft 列表集合
NFT_list = client.trade.nftlists

# 评论表集合
Comments = client.trade.comments

# 点赞表集合
Portfolios_like = client.trade.portfolios_likes

# 收货地址集合
Shipping_address = client.users.shipping_address

# 登录注册集合
User = client.users.information

"""
存放sku信息的数据库
    注意：一个SPU可能会有多个SKU实例
"""
Goods_se_details_sku = client.goods.Goods_se_details_sku



