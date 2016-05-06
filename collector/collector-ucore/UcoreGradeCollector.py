# coding:utf8
# author:winton

import os
import logging
import argparse

from collector import Collector
from config import Config


class UcoreGradeCollector(Collector):
    '''
    从gitlab成绩数据文件收集数据
    '''
    name = 'ucore-collector'

    def __init__(self, config):
        Collector.__init__(self, config.datapool)
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

    def collectAll(self, filename):
        f = open(filename)
        lab = filename.split('.')[1]
        lines = f.readlines()
        for line in lines:
            info = line.split(' ')
            uinfo = [x.decode('utf8') for x in info]
            id = uinfo[0]
            realName = uinfo[1]
            gitUsername = uinfo[2]
            score = uinfo[3].split('/')[0]
            if score == 'no':
                score = 'no score'
                reportScore = 'no score'
                continue
            reportScore = uinfo[4]

            event = {
                'event_type': 'student',
                'topic': 'grade',
                'related': {
                    'course': 'openedx-os',
                    'lab': lab,
                    'student': {
                        'id': id,
                        'labScore': score,
                        'realName': realName,
                        'gitUsername': gitUsername,
                        'reportScore': reportScore,

                    }
                }
            }
            self.sendEvent(event)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='do collecting jobs on gitlab teacher/answer')
    ap.add_argument('-i', help='input filename')
    args = ap.parse_args()

    collector = UcoreGradeCollector(Config)
    collector.collectAll(args.i)
