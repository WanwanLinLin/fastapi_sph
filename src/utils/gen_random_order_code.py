# -*- coding：utf-8 -*-
import time


# 根据日期生成一个随机的支付订单号
def get_order_code():
    #  年月日时分秒+time.time()的后7位
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + str(time.time()).replace('.', '')[-7:])
    return order_no


if __name__ == '__main__':
    print(get_order_code())