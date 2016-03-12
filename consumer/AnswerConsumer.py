# coding:utf8
# author:winton

import logging
import json
from Consumer import Consumer


class StudentAnswerConsumer(Consumer):
    '''
    统计每个学生对每个问题的回答情况
    '''
    def run(self, event, dataDir):
        pass


class QuestionAnswerConsumer(Consumer):
    '''
    统计每个题目的回答状态
    '''
    recodingType = ['single_answer', 'multi_answer', 'true_false']
    typeStr = 'CountStat'
    visualization = 'pie-chart'

    def run(self, event, dataDir):
        question = event['related']['question']
        if question['type'] not in self.recodingType:
            return
        eventContent = event['content']
        studentAnswer = eventContent['answer']
        qStatPath = '%d.stat.json' % question['q_number']
        # 读取并更新qStat
        qStat = self.loadStat(qStatPath)
        if qStat is None:
            logging.info('create new qStat')
            qStat = {
                'question': question,
                'count': 1,
                'stat': {
                    studentAnswer: 1,
                }
            }
        else:
            # 更新qStat
            if studentAnswer in qStat['stat']:
                qStat['stat'][studentAnswer] += 1
            else:
                qStat['stat'][studentAnswer] = 1
            qStat['count'] += 1
        # 保存qStat
        self.saveStat(qStatPath, qStat)
