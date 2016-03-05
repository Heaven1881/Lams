# coding:utf8

import logging


class Config:
    logger = {
        'filename': '/tmp/lams/lams.log',
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        'encoding': 'utf8',
        'level': logging.DEBUG,
    }

    datapool = '/lams/datapool/'
    datapool_new = '/lams/datapool/new'
