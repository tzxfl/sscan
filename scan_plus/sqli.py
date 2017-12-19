# coding=utf-8
# sqli scanner
# by Th1s

from lib.scanner import *
from lib.config import sqli_config


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

    # override
    def genPayload(self):
        payload = []
        for p in self.payload:
            p = p % self.sleep_time
            payload.append(p)
        return payload

    def deepScan(self, scan_param, param_position):
        # 判断网络延迟
        check_param = eval((str(scan_param)).replace("sleep(5)", "user()"))
        score = 0
        for i in xrange(10):
            if(self.doCurl(self.param, self.data, self.header)):
                score += 1
        #网络正常
        if score >= 9:
            if param_position == "get":
                if self.doCurl(check_param, self.data, self.header):
                    flag = not self.doCurl(scan_param, self.data, self.header)
                    return flag
            elif param_position == "post":
                if self.doCurl(self.param, check_param, self.header):
                    flag = not self.doCurl(self.param, scan_param, self.header)
                    return flag
            return False
        else:
            logging.warning("network delay in %s" % self.url)
            return False

    # override
    def doScan(self, q, param_position):
        while not q.empty():
            scan_param = q.get()
            # do scan here
            if param_position == "get":
                flag = not self.doCurl(scan_param, self.data, self.header)
                if flag:
                    # 检测是否误报
                    if self.deepScan(scan_param, param_position):
                        logging.info('sqli in %s, method : "%s", payload : %s' % (self.url, self.method, scan_param))
                        self.scan_result["param"].append(scan_param)
                        self.scan_result["ret"] = 1
                    else:
                        pass
                        # logging.warning("False positives in %s" % self.url)

            elif param_position == "post":
                flag = not self.doCurl(self.param, scan_param, self.header)
                if flag:
                    # 检测是否误报
                    if self.deepScan(scan_param, param_position):
                        logging.info('sqli in %s, method : "%s", payload : %s' % (self.url, self.method, scan_param))
                        self.scan_result["param"].append(scan_param)
                        self.scan_result["ret"] = 1
                    else:
                        pass
                        # logging.warning("False positives in %s" % self.url)
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
