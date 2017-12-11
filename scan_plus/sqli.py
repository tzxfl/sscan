# coding=utf-8
# sqli scanner
# by Th1s

import Queue
import logging
import threading

from lib.scanner import *
from lib.config import sqli_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s')


# sql 注入检测模块
# 利用延时盲注
class SqliScanner(Scanner):

    def __init__(self, *args, **kwargs):

        Scanner.__init__(self, *args, **kwargs)

        # delay     int     请求delay
        # sleep_time int     延时时长
        self.delay = sqli_config['delay']
        self.sleep_time = sqli_config['sleep_time']

        # payload   dict    注入payload
        self.payload = sqli_config['payload']


    # 消费param队列
    # 检测逻辑
    def doScan(self, q):
        while not q.empty():
            scan_param = q.get()
            # do scan here
            if self.param:
                flag = self.doCurl(scan_param, self.data, self.header)
                if flag:
                    # 检测是否误报
                    if self.doCurl(self.param, self.data, self.header):
                        logging.warning("False positives in %s" % self.url)
                        q.task_done()
                        continue
                    logging.info('sqli in %s : %s' % (self.url, scan_param))
                    self.scan_result["param"].append(scan_param)
                    self.scan_result["ret"] = 1

            if self.data:
                flag = self.doCurl(self.param, scan_param, self.header)
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

if __name__ == "__main__":
    method = "post"
    url = "http://www.th1s.cn/test/sqli/1.php"
    header = {}
    param = {"aaa": 1, "bbb": 3}
    data = {"id": "2", "aa": 4}

    test = SqliScanner(method, url, header, param, data)
    test.doWork()

    # result in scan_result
    print test.scan_result
