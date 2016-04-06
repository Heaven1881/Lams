# coding:utf8
# author:winton

import logging


class Config:
    loggerInfo = {
        'filename': '/home/winton/git/Lams/log/collector/collector-grade.log',
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        'encoding': 'utf8',
        'level': logging.INFO,
    }

    datapool = '/home/winton/git/Lams/datapool/new'

    gitConfig = {
        'hostname': '172.16.13.236',
        'port': 80,
        'repo_id': 287,
        'root_token': '9b7YDTxPuN9-ztwchRJ2',
        'ref': 'master',
        'localRepo': '/home/winton/git/answer',
    }
