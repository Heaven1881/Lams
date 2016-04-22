# coding:utf8
# author:winton

import os
import logging
import datetime
import json
import argparse
import urllib

from APICollector import APICollector
from config import Config


class PiazzaCollector(APICollector):
    '''
    负责从piazza平台上收集数据
    '''
    name = 'piazza-collector'

    def __init__(self, config):
        APICollector.__init__(self, config.datapool)
        self.config = config

        # log初始化
        loggingInfo = config.loggerInfo
        logDir, logFile = os.path.split(loggingInfo['filename'])
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        logging.basicConfig(
            level=loggingInfo['level'],
            format=loggingInfo['format'],
            filename=loggingInfo['filename'],
            encoding=loggingInfo['encoding']
        )

        self.collected = 0
        logging.info('collector "%s" starting...' % self.name)

    def piazzaSignUp(self):
        acount = self.config.piazzaAcount
        post = {
            'from': '/signup',
            'email': acount['email'],
            'password': acount['password'],
            'remeber': 'on',
        }
        postEncoded = urllib.urlencode(post).encode()
        url = 'https://piazza.com/class'
        logging.info('login to piazza...')
        self.doPost(url, postEncoded)

    def piazzaGetStatistics(self):
        acount = self.config.piazzaAcount
        post = {
            'method': 'network.get_stats',
            'params': {
                'nid': acount['nid'],
                'anonymize': False,
            }
        }
        postStringtified = json.dumps(post)
        url = 'https://piazza.com/main/api'
        result = self.doPost(url, postStringtified, {'Content-Type': 'application/json'}, datatype='json')
        logging.info('get piazza statistice [error=%s]' % result['error'])
        if result['result']:
            return result['result']
        else:
            return None

    def genEventFromPiazzaData(self, data):
        current = datetime.datetime.now()
        event = {
            'event_type': 'student',
            'time': current.strftime('%Y-%m-%d:%H:%M:%S'),
            'topic': 'piazzadata.all',
            'related': {
                'course': 'openedx-os',
            },
            'content': data,
        }
        return event

    def collectLatest(self):
        logging.info('collect last not suported')
        logging.info('collect %d data' % self.collected)

    def collectAll(self):
        logging.info('collecting statistics data from piazza...')
        self.piazzaSignUp()
        result = self.piazzaGetStatistics()
        if result:
            event = self.genEventFromPiazzaData(result)
            self.collected += 1
            self.sendEvent(event)
        logging.info('collect %d data' % self.collected)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='do collecting jobs on gitlab teacher/answer')
    ap.add_argument('-A', '--all', action='store_true', help='collecting all in localRepo, this is for the first run')
    args = ap.parse_args()

    collector = PiazzaCollector(Config)
    if args.all:
        collector.collectAll()
    else:
        collector.collectLatest()
