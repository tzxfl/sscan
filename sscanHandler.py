# -*- coding: utf-8 -*-

import importlib
import Queue
import time
from multiprocessing import Process

from proxy.proxy import *
from web.web.doRedis.connectRedis import *


def solveUrlParam(rowJson):
    res = {}
    res['method'] = rowJson['method']
    res['header'] = rowJson['headers']

    #无论如何都要处理下url
    query = urlparse.urlparse(rowJson['url']).query
    res['param'] = dict([(k, v[0]) for k, v in urlparse.parse_qs(query.encode("UTF-8")).items()])
    res['data'] = {}
    res['url'] = rowJson['url'].split("?")[0]
    if res['method'].lower() == 'post':
        #目前处理a=1&b=2形式，后续添加更多形式
        if rowJson['body']:
            res['data'] = dict([(k, v[0]) for k, v in urlparse.parse_qs(rowJson['body'].encode("UTF-8")).items()])
    return res


def listenRedis(r, queue, listName):
    #连接redis

    while True:
        if r.llen(listName) > 0:
            row = r.lpop(listName)
            rowJson = json.loads(row)
            saveJson = solveUrlParam(rowJson)
            #入队列
            queue.put(saveJson)
        else:
            time.sleep(1)


def scan(r, queue, scan_modules):
    while True:
        row = queue.get()
        for module_name in scan_modules:
            scan_module = importlib.import_module("scan_plus." + module_name)
            scan_module_class = getattr(scan_module,  module_name + "Scanner")
            scanner = scan_module_class(row['method'], row['url'], row['header'], row['param'], row['data'])
            scanner.doWork()
            if scanner.scan_result['ret'] == 1:
                row['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                row['type'] = module_name
                row['payload'] = scanner.scan_result['param']
                row['message'] = genCompleteHttpMessage(row['method'], row['url'], row['header'], row['param'], row['data'])
                resultJson = json.dumps(row)
                r.rpush(redis_config['http_result_name'], resultJson)


# 生成原始http数据包
def genCompleteHttpMessage(method, url, header, param, data):
    html = ""
    html += method.upper() + " " + url + ("?" if param else "")
    for k, v in param.items():
        html += k + "=" + v + "&"
    html += " HTTP/1.1" + "\n"
    for k, v in header.items():
        html += k + ": " + v + "\n"
    html += "\n"
    for k, v in data.items():
        html += k + "=" + v + "&"
    return html


def importPlus():
    now_dir = os.getcwd()
    filename = os.listdir(now_dir)
    scan_moudle = []
    for name in filename:
        if name.endswith(".py") and name != "__init__.py":
            name = name.split(".")[0]
            scan_moudle.append(name)
    return scan_moudle


def scanWork():
    os.chdir("scan_plus")
    r = redis.Redis(connection_pool=pool)
    # 定义参数
    list_name = redis_config['http_data_name']
    queue = Queue.Queue()

    scan_moudle = importPlus()

    if sys.argv[2:]:
        thread_num = int(sys.argv[2])
    else:
        thread_num = 5

    t1 = threading.Thread(target=listenRedis, args=(r, queue, list_name))
    t1.setDaemon(True)
    t1.start()

    for i in range(thread_num):
        t2 = threading.Thread(target=scan, args=(r, queue, scan_moudle))
        t2.setDaemon(True)
        t2.start()

    print "sscanHandler start..."
    # 使用while True来实现join，实现ctrl+c退出进程
    while True:
        pass

if __name__ == "__main__":

    # 同时启动proxy 和 scan
    p1 = Process(target=proxyStart)
    p1.start()
    p2 = Process(target=scanWork)
    p2.start()

