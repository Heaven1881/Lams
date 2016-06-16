# coding:utf8
# author:winton

import logging


class Config:
    loggerInfo = {
        'filename': '/Lams/log/collector/collector.log',
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        'encoding': 'utf8',
        'level': logging.INFO,
    }

    datapool = '/Lams/datapool/new'

    gitConfig = {
        'hostname': '127.0.0.1',
        'port': 80,
        'repo_id': 287,
        'root_token': '9b7YDTxPuN9-ztwchRJ2',
        'ref': 'master',
        'localRepo': '/var/www/data/answer',
	'user': 'www-data'
    }
