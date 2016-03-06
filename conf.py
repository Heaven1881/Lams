# coding:utf8

import logging


class Config:
    logger = {
        'filename': '/home/winton/git/Lams/log/lams.log',
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        'encoding': 'utf8',
        'level': logging.DEBUG,
    }

    datapool = '/home/winton/git/Lams/datapool/'
    datapool_new = '/home/winton/git/Lams/datapool/new'

    consumer_dir = '/home/winton/git/Lams/consumer'
    consumer_conf_dir = '/home/winton/git/Lams/conf'
    consumer_runtime_dir = '/home/winton/git/Lams/var'
