# coding:utf8
# author:winton

import logging

from Consumer import Consumer


class GitlabCommitCsm(Consumer):
    '''
    收集gitlab平台上的各个project的commit信息
    根据username将其归档
    '''
    typeStr = 'Data'
    visualization = 'none'

    def run(self, event, dataDir):
        related = event['related']

        projectOwner = related.get('owner')
        if projectOwner is None:
            logging.warning('no project owner found, skip this event')
            return

        # 读取统计数据，如果数据不存在则新建
        statPath = '%s.json' % projectOwner['username']
        logging.info('overwrite file [path=%s]' % statPath)
        stat = {
            'title': u'%s gitlab commit 记录' % projectOwner['username'],
            'owner': projectOwner,
            'data': event['content']
        }
        self.saveStat(statPath, stat)
