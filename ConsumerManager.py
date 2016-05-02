# coding:utf8
# author: winton

import logging
import os
import json
import base64
import ConfigParser
import subprocess
from consumer.ConsumerRunner import ConsumerRunner


class ConsumerManager:
    def __init__(self, config):
        self.consumerDir = config.consumer_dir
        self.consumerConfDir = config.consumer_conf_dir
        self.consumerRuntimeDir = config.consumer_runtime_dir
        self.csmRunnerCmd = config.consumer_runner_cmd
        self.consumers = {}

        logging.debug('loading consumer conf in dir "%s"' % config.consumer_dir)
        for filename in os.listdir(config.consumer_conf_dir):
            filePath = os.path.join(config.consumer_conf_dir, filename)
            logging.debug('opening config file [%s]' % filePath)
            try:
                consumerconfig = ConfigParser.ConfigParser()
                consumerconfig.read(filePath)
                self.registerConsumer(consumerconfig)
            except Exception as e:
                logging.exception(str(e))

    def registerConsumer(self, config):
        '''
        从配置中载入consumer
        '''
        for consumer in config.sections():
            try:
                moduleName = config.get(consumer, 'module')
                className = config.get(consumer, 'class')
                collector = config.get(consumer, 'collector')
                topic = config.get(consumer, 'topic')
                self.consumers[consumer] = {
                    'moduleName': moduleName,
                    'className': className,
                    'collector': collector,
                    'topic': topic
                }
            except Exception as e:
                logging.warning('cannot load consumer [%s] [err=%s]' % consumer, str(e))
            else:
                logging.debug('Consumer "%s" loaded' % consumer)

    def getMapConsumer(self, event, fillterClass=None):
        '''
        获取订阅事件的consumer
        '''
        retList = []
        for consumerName in self.consumers:
            consumer = self.consumers[consumerName]
            # 如果用户指定了具体的consumer，则只处理发送给这个consumer的事件信息
            if fillterClass is not None:
                if consumer['className'] != fillterClass[1] or consumer['moduleName'] != fillterClass[0]:
                    continue
            if consumer['collector'] != 'all' and event['collector'] not in consumer['collector']:
                continue
            if consumer['topic'] != 'all' and event['topic'] not in consumer['topic']:
                continue
            retList.append(consumer)
        return retList

    def _sendFromCmd(self, cmdData):
        cmdData['event'] = base64.b64encode(json.dumps(cmdData['event']))
        cmd = self.csmRunnerCmd % cmdData
        logging.debug('run cmd [cmd=%s]' % cmd)
        ret = subprocess.call(cmd.split(' '))
        if ret == 0:
            logging.debug('event is consumed successfully! [consumer=%s]' % (cmdData['className']))

    def _send(self, cmdData):
        cmdData['moduleName'] = 'consumer.' + cmdData['moduleName']
        cr = ConsumerRunner(cmdData)
        cr.do(cmdData['event'])

    def emitEvent(self, event, consumerList):
        '''
        向列表中的consumer发送事件
        '''
        for csm in consumerList:
            dataDir = os.path.join(self.consumerRuntimeDir, 'data.%s' % (csm['className']))
            cmdData = {
                'moduleName': csm['moduleName'],
                'className': csm['className'],
                'event': event,
                'dataDir': dataDir
            }
            # self._sendFromCmd(cmdData)
            self._send(cmdData)
