# coding=utf-8
# sqli scanner
# by Th1s

import Queue
import logging
import threading
import requests
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s')


# 祖先类
class Scanner:

    def __init__(self, *args, **kwargs):

        # method  string  http方法
        # url     string  请求rul
        # header  dict    http头部
        # param   dict    get参数
        # data    dict    post参数
        # cookie  string  cookie

        method, url, header, param, data = args
        self.url = url
        self.method = method
        self.header = header
        self.param = param
        self.data = data

        # string type cookie
        self.cookie = {}

        # delay     int     请求delay
        # sleep_time int    延时时长
        self.delay = 0
        self.sleep_time = 5

        # payload   dict    注入payload
        self.payload = {}

        # 扫描线程数
        self.thread_num = 5

        self.scan_result = {}
        self.scan_result["ret"] = 0
        self.scan_result["param"] = []

    # 生成payload
    # 默认返回self.payload
    def genPayload(self):
        return self.payload

    # 给所有的参数加上 payload
    # return type is dict
    def addPayload(self, param={}, data={}, header={}, cookie={}):
        final_params = {}
        final_data = {}
        final_cookie = {}
        final_header = {}

        payload = self.genPayload()

        if param:
            for k, v in param.iteritems():
                final_params[k] = []
                for p in payload:
                    v1 = str(v) + p
                    final_params[k].append(v1)

        if data:
            for k, v in data.iteritems():
                final_data[k] = []
                for p in payload:
                    v1 = str(v) + p
                    final_data[k].append(v1)

        if header:
            for k, v in header.iteritems():
                final_header[k] = []
                for p in payload:
                    v1 = str(v) + p
                    final_header[k].append(v1)

        if cookie:
            for k, v in cookie.iteritems():
                final_cookie[k] = []
                for p in payload:
                    v1 = str(v) + p
                    final_cookie[k].append(v1)

        return final_params, final_data, final_header, final_cookie

    # curl 方法
    def doCurl(self, param={}, data={}, header={}, cookie={}):
        if self.method.lower() == "get":
            try:
                r = requests.get(self.url, params=param, headers=header, cookies=cookie, timeout=self.sleep_time)
                return False
            except Exception as e:
                return True

        elif self.method.lower() == "post":
            try:
                r = requests.post(self.url, params=param, data=data, headers=header, cookies=cookie, timeout=self.sleep_time)
                return False
            except Exception as e:
                return True

    # 多线程调用doScan
    # 默认只检测 get和post参数
    # result = {"ret":1, "param":["id"]}
    def doWork(self):
        param, data, header, cookie = self.addPayload(self.param, self.data, self.header, self.cookie)
        pqueue = Queue.Queue()
        dqueue = Queue.Queue()

        if param:
            for key, values in param.iteritems():
                for value in values:
                    scan_param = self.param.copy()
                    scan_param[key] = value
                    pqueue.put(scan_param)
        if data:
            for key, values in data.iteritems():
                for value in values:
                    scan_param = self.data.copy()
                    scan_param[key] = value
                    dqueue.put(scan_param)

        for i in range(self.thread_num):
            if pqueue:
                threading.Thread(target=self.doScan, args=(pqueue,)).start()
            if dqueue:
                threading.Thread(target=self.doScan, args=(dqueue,)).start()

        pqueue.join()
        dqueue.join()

    # 具体的检测逻辑
    # q 的类型为队列
    def doScan(self, q):
        pass

if __name__ == "__main__":
    print "Scanner is an ancestor class"
