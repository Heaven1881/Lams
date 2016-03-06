# coding:utf8
# author:winton

import logging
import os

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
        self.cm = ConsumerManager(Config.consumer_dir, Config.consumer_conf_dir)
        logging.info('%d Consumers loaded' % len(self.cm.consumers))
        self.allFile = 0
        self.successFile = 0

        logging.info('Lams starting...')

    def start(self):
        '''
        开始处理指定目录下的数据
        '''
        dataDir = Config.datapool_new
        dataList = os.listdir(dataDir)
        if len(dataList) == 0:
            logging.info('New data not found, exiting...')
            os.system('exit 0')
        logging.info('New data found, dispatching...')
        self.dispatch(dataList, dataDir)
        os.system('exit 0')

    def dispatch(self, dataList, dataDir):
        '''
        分发对应的文件列表
        '''
        for filename in dataList:
            filePath = os.path.join(dataDir, filename)
            try:
                event = Util.loadJsonFile(filePath)
                for csm in self.cm.getMapConsumer(event):
                    logging.info('event "%s" is sent to consumer "%s"' % (filePath, csm))
            except Exception as e:
                logging.exception('Error when dispatching "%s" [%s]' % (filePath, str(e)))
            else:
                self.successFile += 1
            finally:
                self.allFile += 1

        logging.info('Dispatching finish, %d success, %d fail' % (self.successFile, self.allFile - self.successFile))


if __name__ == '__main__':
    test = Lams()
    test.init()
    test.start()
