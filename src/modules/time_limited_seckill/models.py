# encoding:utf-8
from nosql_db import client

# 限时秒杀商品集合
time_limited_seckill_goods = client.seckill.Seckill

# 抢购成功的用户集合
seckill_success_users = client.seckill.seckillSuccess


if __name__ == '__main__':
    # time_limited_seckill_goods.insert_one({
    #     "id": 0,
    #     "goods_name": "iphone 15 pro max ultra origin mini",
    #     "seckill_price": 3999,
    #     "remaining": 100,
    #     "launch_time": "2023-01-01 13:32:26",
    #     "is_delete": 0
    # })
    ...