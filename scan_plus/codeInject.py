# coding=utf-8
# code inject scanner
# by Th1s

from lib.scanner import *
from lib.config import code_inject_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s')


# code inject 检测模块
# 利用延时
class CodeInjectScanner(Scanner):

    def __init__(self, *args, **kwargs):

        Scanner.__init__(self, *args, **kwargs)

        # delay     int     请求delay
        # sleep_time int     延时时长
        self.delay = code_inject_config['delay']
        self.sleep_time = code_inject_config['sleep_time']

        # payload   dict    注入payload
        self.payload = code_inject_config['payload']

    # override
    def genPayload(self):
        payload = []
        for p in self.payload:
            p = p % self.sleep_time
            payload.append(p)
        return payload

    # override
    def doScan(self, q):
        while not q.empty():
            scan_param = q.get()

            # do scan here
            if scan_param.keys() == self.param.keys():
                flag = self.doCurl(scan_param, self.data, self.header)
                if flag:
                    # 检测是否误报
                    if self.doCurl(self.param, self.data, self.header):
                        logging.warning("False positives in %s" % self.url)
                    else:
                        logging.info('code inject in %s : %s' % (self.url, scan_param))
                        self.scan_result["param"].append(scan_param)
                        self.scan_result["ret"] = 1

            else:
                flag = self.doCurl(self.param, scan_param, self.header)
                if flag:
                    # 检测是否误报
                    if self.doCurl(self.param, self.data, self.header):
                        logging.warning("False positives in %s" % self.url)
                    else:
                        logging.info('code inject in %s : %s' % (self.url, scan_param))
                        self.scan_result["param"].append(scan_param)
                        self.scan_result["ret"] = 1
            q.task_done()

if __name__ == "__main__":
    method = "post"
    url = "http://www.th1s.cn/test/sqli/code.php"
    header = {}
    param = {"id": 1, "bbb": 3}
    data = {}
    #data = {"b": "2", "aa": 4}

    test = CodeInjectScanner(method, url, header, param, data)
    test.doWork()

    # result in scan_result
    print test.scan_result