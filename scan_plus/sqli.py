# coding=utf-8
# sqli scanner
# by Th1s

from config import sqli_config
import requests
import logging
import threading
import Queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s')


# sql 注入检测模块
# 利用延时盲注
class SqliScanner:

    def __init__(self, *args, **kwargs):

        # method  string  http方法
        # url     string  请求rul
        # header  dict    http头部
        # param   dict    get参数
        # data    dict    post参数

        method, url, header, param, data = args
        self.url = url
        self.method = method
        self.header = header
        self.param = param
        self.data = data

        # delay     int     请求delay
        # sleep_time int     延时时长
        self.delay = sqli_config['delay']
        self.sleep_time = sqli_config['sleep_time']

        # payload   dict    注入payload
        self.payload = sqli_config['payload']

        self.scan_result = {}
        self.scan_result["ret"] = 0
        self.scan_result["param"] = []

    # 给参数加上payload
    # final_params = {'id': ['1 xor(sleep(3))']}
    def addPayload(self, param={}, data={}):

        final_params = {}
        final_data = {}

        payload = []
        for p in self.payload:
            p = p % self.sleep_time
            payload.append(p)

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

        return final_params, final_data

    def doCurl(self, param, data):
        if self.method.lower() == "get":
            try:
                r = requests.get(self.url, params=param, timeout=self.sleep_time)
                return False
            except Exception as e:
                return True

        elif self.method.lower() == "post":
            try:
                r = requests.post(self.url, params=param, data=data, timeout=self.sleep_time)
                return False
            except Exception as e:
                return True

    # 消费param队列
    def doScan(self, q):
        while not q.empty():
            scan_param = q.get()
            # do scan here
            if self.param:
                flag = self.doCurl(scan_param, self.data)
                if flag:
                    # 检测是否误报
                    if self.doCurl(self.param, self.data):
                        logging.warning("False positives in %s" % self.url)
                        q.task_done()
                        continue
                    logging.info('sqli in %s : %s' % (self.url, scan_param))
                    self.scan_result["param"].append(scan_param)
                    self.scan_result["ret"] = 1

            if self.data:
                flag = self.doCurl(self.param, scan_param)
                if flag:
                    # 检测是否误报
                    if self.doCurl(self.param, self.data):
                        logging.warning("False positives in %s" % self.url)
                        q.task_done()
                        continue
                    logging.info('sqli in %s : %s' % (self.url, scan_param))
                    self.scan_result["param"].append(scan_param)
                    self.scan_result["ret"] = 1
            q.task_done()

    # result = {"ret":1, "param":["id"]}
    def doWork(self):
        param, data = self.addPayload(self.param, self.data)
        pqueue = Queue.Queue()
        dqueue = Queue.Queue()

        if self.param:
            for key, values in param.iteritems():
                for value in values:
                    scan_param = {}
                    scan_param[key] = value
                    pqueue.put(scan_param)
        if self.data:
            for key, values in data.iteritems():
                for value in values:
                    scan_param = {}
                    scan_param[key] = value
                    dqueue.put(scan_param)

        for i in range(10):
            t1 = threading.Thread(target=self.doScan, args=(pqueue,)).start()
            t2 = threading.Thread(target=self.doScan, args=(dqueue,)).start()

        pqueue.join()
        dqueue.join()

if __name__ == "__main__":
    method = "post"
    url = "http://www.th1s.cn/test/sqli/1.php"
    header = {}
    param = {"aaa": 1}
    data = {"id": "2"}

    test = SqliScanner(method, url, header, param, data)
    test.doWork()

    # result in scan_result