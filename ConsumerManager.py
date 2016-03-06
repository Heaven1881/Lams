# coding:utf8
# author: winton

import logging
import os
import ConfigParser


class ConsumerManager:
    def __init__(self, consumerDir, consumerConfDir):
        self.consumerDir = consumerDir
        self.consumerConfDir = consumerConfDir
        self.consumers = {}

        logging.debug('loading consumer conf in dir "%s"' % consumerDir)
        for filename in os.listdir(consumerConfDir):
            filePath = os.path.join(consumerConfDir, filename)
            logging.debug('opening config file [%s]' % filePath)
            try:
                config = ConfigParser.ConfigParser()
                config.read(filePath)
                self.registerConsumer(config)
            except Exception as e:
                logging.exception(str(e))

    def registerConsumer(self, config):
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

    def getMapConsumer(self, event):
        '''
        将事件发送给consumer
        '''
        retList = []
        for consumerName in self.consumers:
            consumer = self.consumers[consumerName]
            logging.debug('map consumer [event={"collector":"%s","topic":"%s"}] [consumer={"collector":"%s","topic":"%s"}]' % (
                event['collector'],
                event['topic'],
                consumer['collector'],
                consumer['topic'],
            ))
            if not event['collector'] in consumer['collector']:
                continue
            if not event['topic'] in consumer['topic']:
                continue
            retList.append(consumer)
        return retList
