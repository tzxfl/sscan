# coding=utf-8
# code&command inject scanner
# by Th1s

import logging

from lib.config import code_inject_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s')


# sql 注入检测模块
# 利用延时盲注
class CodeInjectScanner:

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
        self.delay = code_inject_config['delay']
        self.sleep_time = code_inject_config['sleep_time']

        # payload   dict    注入payload
        self.payload = code_inject_config['payload']

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