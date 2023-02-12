# encoding:utf-8
from typing import Any, Dict

import pika
import random


def send_message(num: Dict):
    # f"pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@localhost/{RABBITMQ_VHOST}"
    # 新建连接，rabbitmq安装在本地则hostname为'localhost'
    parameters = pika.ConnectionParameters(host="192.168.42.128", virtual_host="my_vhost")
    connection = pika.BlockingConnection(parameters)

    # 创建通道
    channel = connection.channel()
    # 声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行
    channel.queue_declare(queue='PreferentialGoods')

    body = f'{num}'
    # routing_key在使用匿名交换机的时候才需要指定，表示发送到哪个队列
    channel.basic_publish(exchange='', routing_key='PreferentialGoods', body=body)
    connection.close()


if __name__ == '__main__':
    send_message({"num": 999})