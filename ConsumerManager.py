# coding:utf8
# author: winton

import logging
import os
import json
import base64
import ConfigParser
import subprocess


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
            if fillterClass is not None:
                if consumer['className'] != fillterClass[1] or consumer['moduleName'] != fillterClass[0]:
                    continue
            if not event['collector'] in consumer['collector']:
                continue
            if not event['topic'] in consumer['topic']:
                continue
            retList.append(consumer)
        return retList

    def emitEvent(self, event, consumerList):
        '''
        向列表中的consumer发送事件
        '''
        for csm in consumerList:
            try:
                dataDir = os.path.join(self.consumerRuntimeDir, 'data.%s' % (csm['className']))
                cmdData = {
                    'modelName': csm['moduleName'],
                    'className': csm['className'],
                    'event': base64.b64encode(json.dumps(event)),
                    'dataDir': dataDir
                }
                cmd = self.csmRunnerCmd % cmdData
                logging.debug('run cmd [cmd=%s]' % cmd)
                ret = subprocess.call(cmd.split(' '))
                if ret == 0:
                    logging.debug('event is consumed successfully! [consumer=%s] [event=%s]' % (csm, event))
            except Exception as e:
                logging.exception('error when running consumer "%s": %s' % (csm, str(e)))
