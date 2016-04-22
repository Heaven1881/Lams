# coding:utf8
# author:winton

import socket
import urllib2
import cookielib
import json
import logging

from collector import Colllector


class APICollector(Colllector):
    '''
    通过调用API收集数据
    '''
    def __init__(self, datapool):
        Colllector.__init__(self, datapool)

        # 初始化opener
        cookiejar = cookielib.CookieJar()
        processor = urllib2.HTTPCookieProcessor(cookiejar)
        opener = urllib2.build_opener(processor)
        urllib2.install_opener(opener)

        self.opener = opener

    def doPost(self, url, body, header={}, datatype='text'):
        socket.setdefaulttimeout(30)

        logging.debug('request [url=%s] [body=%s] [header=%s]' % (url, body, str(header)))
        req = urllib2.Request(url, body, header)
        response = self.opener.open(req)
        result = response.read()

        if datatype == 'json':
            return json.loads(result)
        else:
            return result
