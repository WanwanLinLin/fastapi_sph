# -*- coding：utf-8 -*-
import redis

pool = redis.ConnectionPool(host="172.23.75.30", port=6379, db=3, decode_responses=True)
pool_2 = redis.ConnectionPool(host="172.23.75.30", port=6379, db=2, decode_responses=True)
pool_3 = redis.ConnectionPool(host="172.23.75.30", port=6379, db=1, decode_responses=True)
pool_4 = redis.ConnectionPool(host="172.23.75.30", port=6379, db=4, decode_responses=True)

# # 下班后的redis
# pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=3, decode_responses=True)
# pool_2 = redis.ConnectionPool(host="127.0.0.1", port=6379, db=2, decode_responses=True)
# pool_3 = redis.ConnectionPool(host="127.0.0.1", port=6379, db=1, decode_responses=True)
# pool_4 = redis.ConnectionPool(host="127.0.0.1", port=6379, db=4, decode_responses=True)


# 连接 redis 数据库
# 用于存储jwt_access
r = redis.Redis(connection_pool=pool)
# 用于存储提交订单的信息以及每位用户所拥有的订单
r_2 = redis.Redis(connection_pool=pool_2)
# 用户存储后台管理人员的X-API-KEY
r_3 = redis.Redis(connection_pool=pool_3)
# 存储手机验证码
r_4 = redis.Redis(connection_pool=pool_4)


if __name__ == '__main__':
    r_4.set('19178521060', '1234')