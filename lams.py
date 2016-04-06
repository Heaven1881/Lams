# coding:utf8
# author:winton

import logging
import os
import datetime
import argparse

from conf import Config
from util import Util
from ConsumerManager import ConsumerManager


class Lams:
    '''
    控制数据收集的主要流程
    '''

    def init(self):
        '''
        读取配置并完成初始化
        '''
        loggerConfig = Config.logger
        # 检查日志文件夹是否存在
        logDir = os.path.split(loggerConfig['filename'])[0]
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        # 日志配置
        logging.basicConfig(
            level=loggerConfig['level'],
            format=loggerConfig['format'],
            filename=loggerConfig['filename'],
            encoding=loggerConfig['encoding']
        )

        # 载入consumer
        self.cm = ConsumerManager(Config)
        logging.info('%d Consumers loaded' % len(self.cm.consumers))
        self.allFile = 0
        self.successFile = 0

        logging.info('Lams starting...')

    def startForNew(self, move_after_dispatch=True):
        '''
        开始处理指定目录下的数据
        '''
        dataDir = Config.datapool_new
        dataList = os.listdir(dataDir)
        if len(dataList) == 0:
            logging.info('New data not found, exiting...')
            os.system('exit 0')
        logging.info('New data found, dispatching...')
        for filename in dataList:
            self.dispatch(filename, dataDir, move_after_dispatch)
        logging.info('Dispatching finish, %d success, %d fail' % (self.successFile, self.allFile - self.successFile))
        os.system('exit 0')

    def startForAll(self, classInfo=None):
        '''
        重新处理所有数据
        '''
        if classInfo is not None:
            logging.info('dispatch for class [%s]' % classInfo)
        logging.info('dispatch all data...')
        for parent, dirnames, filenames in os.walk(Config.datapool):
            for filename in filenames:
                self.dispatch(filename, parent, False, classInfo=classInfo)
        logging.info('Dispatching finish, %d success, %d fail' % (self.successFile, self.allFile - self.successFile))
        os.system('exit 0')

    def dispatch(self, filename, dataDir, move_after_dispatch=True, classInfo=None):
        '''
        分发对应的文件列表
        '''
        filePath = os.path.join(dataDir, filename)
        try:
            event = Util.loadJsonFile(filePath)
            consumers = self.cm.getMapConsumer(event, classInfo)
            for csm in consumers:
                logging.info('event "%s" is sending to consumer "%s"' % (filePath, csm))
            self.cm.emitEvent(event, consumers)
        except Exception as e:
            logging.exception('Error when dispatching "%s" [%s]' % (filePath, str(e)))
        else:
            self.successFile += 1
            # 将已处理的文件移动到指定文件夹
            if move_after_dispatch:
                t = datetime.datetime.now()
                today = t.strftime('%Y-%m-%d')
                newDir = '%s/%s' % (Config.datapool, today)
                if not os.path.exists(newDir):
                    os.makedirs(newDir)
                newFilePath = '%s/%s' % (newDir, filename)
                logging.debug('moving [src=%s] [dst=%s]' % (filePath, newFilePath))
                os.rename(filePath, newFilePath)
        finally:
            self.allFile += 1

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='do dispatching jobs')
    ap.add_argument('-A', '--all', action='store_true', help='dispatch all history data and new data')
    ap.add_argument('-c', help='dispatch all but just dispatch to one class, use it in this form [moduleName:className]')
    args = ap.parse_args()

    test = Lams()
    test.init()
    if args.all:
        test.startForAll()
    elif args.c is not None:
        test.startForAll(args.c.split(':'))
    else:
        test.startForNew()
