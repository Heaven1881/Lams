# coding:utf8

import logging


class Config:
    logger = {
        'filename': '/Lams/log/lams.log',
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        'encoding': 'utf8',
        'level': logging.INFO,
    }

    datapool = '/Lams/datapool/'
    datapool_new = '/Lams/datapool/new'

    consumer_dir = '/Lams/consumer'
    consumer_conf_dir = '/Lams/conf'
    consumer_runtime_dir = '/Lams/var'
    consumer_runner_cmd = 'python /Lams/consumer/ConsumerRunner.py -m %(moduleName)s -c %(className)s -e \'%(event)s\' -d %(dataDir)s'
