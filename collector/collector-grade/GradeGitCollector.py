# coding: utf8
# author: winton

import logging
import re
import datetime
import os
import argparse

from GitlabCollector import GitlabCollector
from config import Config


class GradeGitCollector(GitlabCollector):
    '''
    负责从gitlab上teacher/answer库中收集学生的回答信息
    '''
    name = 'grade-collector'

    def __init__(self, config):
        GitlabCollector.__init__(self, config.datapool, config.gitConfig)
        self.config = config
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

    def genEventFromGradeInfo(self, gradeInfo):
        t = datetime.datetime.now()
        createtime = t.strftime('%Y-%m-%d:%H:%M:%S')
        event = {
            'event_type': 'student',
            'time': createtime,
            'topic': 'grade',
            'related': {
                'student': gradeInfo['student'],
                'question': {
                    'q_number': gradeInfo['q_number'],
                },
                'course': 'openedx-os',
            },
            'content': {
                'score': gradeInfo['score']
            }
        }
        return event

    def collectLatest(self):
        '''
        收集最近的信息
        '''
        self.updateLoaclRepo()
        modifiedList = self.getModifiedFilesAfterLastCommit()
        logging.info('find %d lastest modify' % len(modifiedList))
        if len(modifiedList) == 0:
            return
        for filename in modifiedList:
            match = re.match('[0-9a-z]{2}/[^/]+/[0-9]{1,4}/[0-9]{1,4}\.graded\.json', filename)
            if match:
                logging.debug('modified file [path=%s]' % filename)
                gradeInfo = self.loadJsonFromLocalRepo(filename)
                event = self.genEventFromGradeInfo(gradeInfo)
                self.sendEvent(event)
                self.collected += 1
                logging.info('collect file [path=%s]' % filename)
            else:
                logging.debug('skip file [path=%s]' % filename)
        logging.info('collect %d data' % self.collected)
        self.recodeLastCommit()

    def collectAll(self):
        '''
        收集所有信息
        '''
        logging.info('collecting all data from local repo [path=%s]' % self.config.gitConfig['localRepo'])
        for parent, dirnames, filenames in os.walk(self.config.gitConfig['localRepo']):
            for filename in filenames:
                filepath = os.path.join(parent, filename)
                if re.search('[0-9a-z]{2}/[^/]+/[0-9]{1,4}/[0-9]{1,4}\.graded\.json$', filepath):
                    gradeInfo = self.loadJsonFromLocalRepo(filepath)
                    event = self.genEventFromGradeInfo(gradeInfo)
                    self.collected += 1
                    self.sendEvent(event)
                else:
                    logging.debug('ignore file [%s]' % filepath)
        logging.info('collect %d data' % self.collected)
        self.recodeLastCommit()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='do collecting jobs on gitlab teacher/answer')
    ap.add_argument('-A', '--all', action='store_true', help='collecting all in localRepo, this is for the first run')
    args = ap.parse_args()

    collector = GradeGitCollector(Config)
    if args.all:
        collector.collectAll()
    else:
        collector.collectLatest()
