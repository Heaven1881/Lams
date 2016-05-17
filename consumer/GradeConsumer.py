# coding:utf8
# author:winton

import logging
from Consumer import Consumer


class ScoreCsm(Consumer):
    '''
    统计每个学生的得分，包括:
      1. 在线练习每题的分数
      2. 实验每个lab的分数（实验得分，报告得分）
    '''
    typeStr = 'Data'
    visualization = 'none'

    def run(self, event, dataDir):
        related = event['related']

        student = related.get('student')
        if student is None:
            logging.warning('no student info found, skiping...')
            return

        # 判断事件的类型
        gradeType = None
        gradeType = 'openedx-quiz' if related.get('question') is not None else gradeType
        gradeType = 'ucore-lab' if related.get('lab') is not None else gradeType

        # 读取统计数据, 如果这是第一次读取，则新建统计数据文件
        if gradeType is 'openedx-quiz':
            statPath = '%s.json' % student['email']
            name = student['email']
        elif gradeType is 'ucore-lab':
            statPath = 'ucore.%s.json' % student['gitUsername']
            name = student['gitUsername']
        else:
            logging.warning('unkown grade type')
            return

        stat = self.loadStat(statPath)
        if stat is None:
            logging.info('create new stat file [path=%s]' % statPath)
            stat = {
                'title': u'%s 得分统计' % name,
                'student': student,
                'data': {
                    'openedx-quiz': {},
                    'ucore-lab': {},
                }
            }

        # 统计成绩信息
        content = event['content']
        if gradeType is 'openedx-quiz':
            question = related['question']
            gradeItem = {question['q_number']: content}
            stat['data']['openedx-quiz'].update(gradeItem)
        if gradeType is 'ucore-lab':
            lab = related['lab']
            gradeItem = {lab: content}
            stat['data']['ucore-lab'].update(gradeItem)

        # 保存信息
        self.saveStat(statPath, stat)


class UcoreScoreCsm(Consumer):
    '''
    根据lab统计每个lab的实验得分分布
    '''
    typeStr = 'CountStat'
    visualization = 'pie'

    def run(self, event, dataDir):
        related = event['related']
        content = event['content']
        lab = related['lab']
        statPath = '%s.json' % lab
        stat = self.loadStat(statPath)
        if stat is None:
            stat = {
                'title': u'%s 实验成绩分布' % lab,
                'xTitle': u'得分',
                'yTitle': u'人数',
                'stat': [],
            }
        labScore = content['labScore']
        statItem = self.getJsonInList(stat['stat'], labScore)
        if statItem is None:
            statItem = {'name': labScore, 'y': 0}
        statItem['y'] += 1
        self.updateJsonInList(stat['stat'], statItem)
        self.saveStat(statPath, stat)


