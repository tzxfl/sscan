# coding=utf-8
# django view

import json

from django.http import HttpResponse
from django.shortcuts import render
from doRedis.connectRedis import *
from doRedis.config import redis_config


def index(request):
    return render(request, "test.html")


# 获取scan job
def getJob(request):

    # 获取redis实例
    r = getRedisInstance()
    http_data_name = redis_config["http_data_name"]
    job_num = r.llen(http_data_name)

    return HttpResponse(job_num)


# 获取scan result
def getResult(request):

    # 获取redis实例
    r = getRedisInstance()
    http_result_name = redis_config["http_result_name"]
    result_num = r.llen(http_result_name)

    result_list = r.lrange(redis_config["http_result_name"], 0, -1)
    for i in range(result_num):
        result_list[i] = json.loads(result_list[i])
    final_result = json.dumps({"result_num": result_num, "result_list": result_list})

    return HttpResponse(final_result)
