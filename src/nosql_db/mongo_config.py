# -*- coding：utf-8 -*-
import pymongo

# 本地服务器
client = pymongo.MongoClient("172.23.75.30", 27017)
# 下班后的mongo
# client = pymongo.MongoClient("127.0.0.1", 27017)
