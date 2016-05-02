# coding:utf8
# author:winton

import json
import logging
import codecs
import os
import time
import hashlib


class Colllector:
    '''
    collector的基类，提供基础的功能
    '''
    def __init__(self, datapoolDir):
        self.datapool = datapoolDir

    def sendEvent(self, event):
        event['collector'] = self.name
        filename = '%(topic)s.%(timestamp)d.%(contentHash)s.json'
        filename = filename % {
            'topic': event['topic'],
            'timestamp': int(time.time()),
            'contentHash': hashlib.new('md5', json.dumps(event)).hexdigest()[:8]
        }
        filepath = os.path.join(self.datapool, filename)
        filepath = self.ensureNotExists(filepath)
        self.saveJsonToFile(filepath, event)

    def ensureNotExists(self, filepath):
        '''
        确保filepath指向的文件不存在，如果存在则修改名字并返回
        '''
        if not os.path.exists(filepath):
            return filepath
        else:
            logging.warning('conflict filepath "%s"' % filepath)
            return self.ensureNotExists('%s.json' % filepath)

    def saveJsonToFile(self, filepath, event):
        f = codecs.open(filepath, 'w', 'utf8')
        try:
            f.write(json.dumps(event, ensure_ascii=False, indent=4, separators=(',', ':')))
        finally:
            f.close()

    def loadJsonFromFile(self, filepath):
        if not os.path.exists(filepath):
            logging.warning('loading a file not exists [path=%s]' % filepath)
            return None
        f = codecs.open(filepath, encoding='utf8')
        jsonStr = f.read()
        f.close()
        if jsonStr:
            return json.loads(jsonStr)
        else:
            logging.warning('read None content')
            return None
