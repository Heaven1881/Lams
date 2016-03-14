# coding:utf8
# author:winton

import logging


class Config:
    loggerInfo = {
        'filename': '/home/winton/git/Lams/log/collector/collector.log',
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        'encoding': 'utf8',
        'level': logging.DEBUG,
    }

    datapool = '/home/winton/git/Lams/datapool/new'

    gitConfig = {
        'hostname': 'http://172.16.13.236',
        'port': 80,
        'repo_id': 287,
        'root_token': 'xxxxxxxxxxxxxxxxxxxxx',
        'ref': 'master-quizzes2',
        'localRepo': '/home/winton/git/answer',
    }
