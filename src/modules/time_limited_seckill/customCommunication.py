# encoding:utf-8
import logging

import faker
import json
import pika
import ast
from nosql_db import client
from datetime import datetime
from models import time_limited_seckill_goods, seckill_success_users

logging.basicConfig(level=logging.INFO)  # 配置日志


class ReceiveMessageCenter(object):
    def __init__(self):
        self.response = None
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='192.168.42.128', virtual_host="my_vhost"))

        self.channel = self.connection.channel()

        # 定义接收返回消息的队列
        result = self.channel.queue_declare(queue='PreferentialGoods')
        self.callback_queue = result.method.queue

        self.channel.basic_consume(on_message_callback=self.on_response,
                                   queue='PreferentialGoods', auto_ack=True)

    # 定义接收到返回消息的处理方法
    def on_response(self, ch, method, props, body):
        info = str(body, "utf-8")
        info = ast.literal_eval(info)
        goods_info = time_limited_seckill_goods.find_one({
            "goods_name": info["goods_name"],
            "seckill_price": info["seckill_price"]})
        if goods_info["remaining"] <= 0:
            return
        time_limited_seckill_goods.update_one({"goods_name": info["goods_name"]},
                                              {"$inc": {"remaining": -1}})
        # 创建一个自增长id
        id_list = list(seckill_success_users.find().sort("id", -1))
        if not id_list:
            id_ = 1
        else:
            id_ = id_list[0]["id"] + 1
        seckill_success_users.insert_one({"id": id_, "username": info["username"],
                                          "goods_name": info["goods_name"],
                                          "seckill_price": info["seckill_price"],
                                          "order_time": datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
                                          "is_delete": 0})
        logging.info("purchase success !")

    def request(self):
        self.response = None
        # 接收返回的数据
        while self.response is None:
            self.connection.process_data_events()
        return self.response


if __name__ == '__main__':
    logging.info("starting receive message...")
    center = ReceiveMessageCenter()
    response = center.request()
