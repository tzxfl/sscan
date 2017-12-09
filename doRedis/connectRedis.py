# coding=utf-8
# redis connector
# by Th1s

import redis
from config import redis_config

host = redis_config["host"]
port = redis_config["port"]
password = redis_config["password"]


# 连接池模式，使用connection pool来管理对一个redis server的所有连接
def connectRedis():
    pool = redis.ConnectionPool(host=host, port=port, password=password, db=0)
    return pool

