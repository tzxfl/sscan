# -*- coding: utf-8 -*-

import redis
from doRedis.config import redis_config
from doRedis.connectRedis import connectRedis
import sys
import time
import Queue
import json
import urlparse
import urllib
from scan_plus.sqli import *
import threading


def solveUrlParam(rowJson):
    res = {}
    res['url'] = rowJson['url']
    res['method'] = rowJson['method']
    res['header'] = rowJson['headers']

    #无论如何都要处理下url
    query = urlparse.urlparse(res['url']).query
    res['param'] = dict([(k,v[0]) for k,v in urlparse.parse_qs(query.encode("UTF-8")).items()])
    res['data'] = {}

    if res['method'].lower() == 'post':
        #目前处理a=1&b=2形式，后续添加更多形式
        if rowJson['body']:
            res['data'] = dict([(k,v[0]) for k,v in urlparse.parse_qs(rowJson['body'].encode("UTF-8")).items()])
    return res

def listenRedis(r, queue, listName):
    #连接redis


    while 1:
        if r.llen(listName) > 0:
            row = r.lpop(listName)
            rowJson = json.loads(row)
            saveJson = solveUrlParam(rowJson)
            #入队列
            queue.put(saveJson)
        else:
            time.sleep(1)

def scan(r, queue, scanModule):
    while 1:
        row = queue.get()
        for moduleName in scanModule:
            scanner = SqliScanner(row['method'], row['url'], row['header'], row['param'], row['data'])
            scanner.doWork()
            #scanner.scan_result['ret'] = 1
            #scanner.scan_result['param'] = '1'
            if scanner.scan_result['ret'] == 1:
                row['payload'] = scanner.scan_result['param']
                resultJson = json.dumps(row)
                r.rpush(redis_config['http_result_name'], resultJson)
            #print 'done'
        #time.sleep(0.1)

if __name__ == "__main__":
    pool = connectRedis()
    r = redis.Redis(connection_pool=pool)
    #定义参数
    listName = redis_config['http_data_name']
    queue = Queue.Queue()
    scanModule = ['sqli']

    if sys.argv[1:]:
        threadNum = int(sys.argv[1])
    else:
        threadNum = 5

    t1 = threading.Thread(target=listenRedis, args=(r, queue, listName))
    t1.setDaemon(True)
    t1.start()

    for i in range(threadNum):
        t2 = threading.Thread(target=scan, args=(r, queue, scanModule))
        t2.setDaemon(True)
        t2.start()

    print "Handler start..."
    # 使用while True来实现join，实现ctrl+c退出进程
    while True:
        pass

