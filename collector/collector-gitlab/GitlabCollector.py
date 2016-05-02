# coding:utf8
# author:winton

import os
import logging
import datetime
import argparse

from APICollector import APICollector
from config import Config


class GitlabCollector(APICollector):
    '''
    负责收集学生在gitlab的统计信息
    '''
    name = 'gitlab-collector'

    def __init__(self, config):
        APICollector.__init__(self, config.datapool)
        self.config = config

        # log初始化
        loggingInfo = config.loggerInfo
        logDir, logFile = os.path.split(loggingInfo['filename'])
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        logging.basicConfig(
            level=loggingInfo['level'],
            format=loggingInfo['format'],
            filename=loggingInfo['filename'],
            encoding=loggingInfo['encoding']
        )

        self.collected = 0
        logging.info('collector "%s" starting...' % self.name)

    def initProjectList(self, jsonFilename='projects.json'):
        '''
        获取teacher下的所有库，这些库都是学生的实验代码库
        检查文件jsonFilename是否存在，如果存在则直接读取本地，否则读取网络
        '''
        projects = self.loadJsonFromFile(jsonFilename)
        if projects is None:
            url = 'http://172.16.13.236/api/v3/projects?private_token=%(root_token)s&per_page=%(per_page)d' % {
                'root_token': self.config.rootToken,
                'per_page': 300,
            }
            projects = self.doGet(url, datatype='json')
            # 检查获取的project list是否合理
            result = 'success' if type(projects) is list else projects['message']
            logging.info('getting project list from gitlab... %s' % result)
            if result is 'success':
                self.saveJsonToFile(jsonFilename, projects)
        return projects

    def getCommitList(self, projectId, user):
        '''
        获取projectId 对应的commit记录，只获取用户名user的commit记录
        '''
        url = 'http://172.16.13.236/api/v3/projects/%(project_id)s/repository/commits?private_token=%(root_token)s&per_page=%(per_page)d' % {
            'root_token': self.config.rootToken,
            'project_id': projectId,
            'per_page': 100,
        }
        commits = self.doGet(url, datatype='json')
        # 检查是否成功
        result = 'success' if type(commits) is list else commits['message']
        logging.info('loading commits for user %s... %s' % (user, result))
        if result is 'success':
            # 只获取指定用户的commit
            return [c for c in commits if c['author_name'] == user]
        else:
            raise Exception('error while reading commits %s' % result)

    def genEventFromCommitList(self, commitList, owner):
        current = datetime.datetime.now()
        event = {
            'event_type': 'student',
            'time': current.strftime('%Y-%m-%d:%H:%M:%S'),
            'topic': 'gitlab.commits.all',
            'related': {
                'course': 'openedx-os',
                'owner': owner
            },
            'content': commitList,
        }
        return event

    def collectLatest(self):
        logging.info('collect lastest not suported')
        self.collectAll()

    def collectAll(self):
        logging.info('collecting all statistics data from gitlab...')
        projects = self.initProjectList()
        for project in projects:
            try:
                commitList = self.getCommitList(project['id'], project['owner']['name'])
                logging.info('the number of commits is %d' % len(commitList))
                if len(commitList) > 0:
                    event = self.genEventFromCommitList(commitList, project['owner'])
                    self.collected += 1
                    self.sendEvent(event)
                    logging.debug('sending event...')
            except Exception as e:
                logging.warning('error while collecting data [owner=%s] [e=%s]' % (project['owner']['name'], e))
        logging.info('collect %d data' % self.collected)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='do collecting jobs on gitlab teacher/answer')
    ap.add_argument('-A', '--all', action='store_true', help='collecting all in localRepo, this is for the first run')
    args = ap.parse_args()

    collector = GitlabCollector(Config)
    if args.all:
        collector.collectAll()
    else:
        collector.collectLatest()
