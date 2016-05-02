# coding:utf8
# author:winton

import re
import os
import logging
import argparse

from GitlabCollector import GitlabCollector
from config import Config


class AnswerGitCollector(GitlabCollector):
    '''
    负责从gitlab上teacher/answer库中收集学生的回答信息
    '''
    name = 'answer-collector'

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

    def getLastestMdfInfo(self):
        '''
        deprecated
        '''
        commits = self.getCommitsAfterLastCommit(perPage=500)
        mdfJsonList = []
        for commit in commits:
            commitMsg = commit['message']
            match = re.match('(\w+) ([0-9a-z]{2})/([^/]+)/([0-9]{1,4})/[0-9]{1,4}\.json', commitMsg)
            if match:
                mdfJsonList.append(match.groups())
            else:
                logging.debug('mismatch commit message [%s]' % commitMsg)
        return mdfJsonList

    def genEventFromAnswerInfo(self, answerInfo):
        event = {
            'event_type': 'student',
            'time': answerInfo['answer'][-1]['time'],
            'topic': 'answer',
            'related': {
                'student': answerInfo['student'],
                'question': {
                    'q_number': answerInfo['question']['q_number'],
                    'type': answerInfo['question']['type'],
                },
                'course': 'openedx-os',
            },
            'content': {
                'desc': 'student({student}) answer question({question}) in course({course})',
                'answer': answerInfo['answer'][-1]['answer'],
            }
        }
        return event

    def collectLatest(self):
        self.updateLoaclRepo()
        modifiedList = self.getModifiedFilesAfterLastCommit()
        logging.info('find %d lastest modify' % len(modifiedList))
        if len(modifiedList) == 0:
            return
        for filename in modifiedList:
            match = re.match('[0-9a-z]{2}/[^/]+/[0-9]{1,4}/[0-9]{1,4}\.json', filename)
            if match:
                logging.debug('modified file [path=%s]' % filename)
                answerInfo = self.loadJsonFromLocalRepo(filename)
                if answerInfo is None:
                    continue
                event = self.genEventFromAnswerInfo(answerInfo)
                self.sendEvent(event)
                self.collected += 1
            else:
                logging.debug('skip file [path=%s]' % filename)
        logging.info('collect %d data' % self.collected)
        self.recodeLastCommit()

    def _collectLatest(self):
        lastestList = self.getLastestMdfInfo()
        logging.info('find %d lastest modify' % len(lastestList))
        if len(lastestList) != 0:
            self.updateLoaclRepo()
        for op, emailHash, username, qNo in lastestList:
            if op in ['create', 'update']:
                answerInfo = self.loadJsonFromLocalRepo('%(emailHash)s/%(username)s/%(qNo)d/%(qNo)d.json' % {
                    'emailHash': emailHash,
                    'username': username,
                    'qNo': int(qNo)
                })
                event = self.genEventFromAnswerInfo(answerInfo)
                self.collected += 1
                logging.debug('sending event [event=%s]' % str(event))
                self.sendEvent(event)
            else:
                logging.warning('unknown operation [%s]' % op)
        logging.info('collect %d data' % self.collected)
        self.recodeLastCommit()

    def collectAll(self):
        '''
        收集本地库的所有信息，并记录最新的commit信息
        '''
        logging.info('collecting all data from local repo [path=%s]' % self.config.gitConfig['localRepo'])
        for parent, dirnames, filenames in os.walk(self.config.gitConfig['localRepo']):
            for filename in filenames:
                filepath = os.path.join(parent, filename)
                if re.search('[0-9a-z]{2}/[^/]+/[0-9]{1,4}/[0-9]{1,4}.json$', filepath):
                    answerInfo = self.loadJsonFromLocalRepo(filepath)
                    event = self.genEventFromAnswerInfo(answerInfo)
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

    collector = AnswerGitCollector(Config)
    if args.all:
        collector.collectAll()
    else:
        collector.collectLatest()
