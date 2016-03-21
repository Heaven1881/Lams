# coding:utf8
# author:winton

import logging
import json
import time
from Consumer import Consumer


class StudentAnswerConsumer(Consumer):
    '''
    统计每个学生对每个问题的回答情况
    '''
    def run(self, event, dataDir):
        pass


class StudentAnswerHeatmapConsumer(Consumer):
    '''
    统计学生整体在不同时候的回答练习情况
    '''
    typeStr = 'HeatmapStat'
    visualization = 'heatmap'

    def run(self, event, dataDir):
        timeStr = event['time']
        statpath = 'answerheatmap.stat.json'

        tm = time.strptime(timeStr, '%Y-%m-%d:%H:%M:%S')
        tm_date = '%d-%d-%d' % (tm.tm_year, tm.tm_mon, tm.tm_mday)
        tm_hour = tm.tm_hour

        # 读取并更新stat
        stat = self.loadStat(statpath)
        if stat is None:
            logging.info('create new stat')
            stat = {
                'title': u'回答情况时间热力分布图',
                'stat': [
                    [tm_date, tm_hour, 1],
                ],
            }
        else:
            # 更新stat
            new = True
            for statItem in stat['stat']:
                if tm_date == statItem[0] and tm_hour == statItem[1]:
                    statItem[2] += 1
                    new = False
                    break
            if new:
                stat['stat'].append([tm_date, tm_hour, 1])
        self.saveStat(statpath, stat)


class QuestionAnswerConsumer(Consumer):
    '''
    统计每个题目的回答状态
    '''
    recodingType = ['single_answer', 'multi_answer', 'true_false']
    typeStr = 'CountStat'
    visualization = 'pie'

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
                'title': u'第%d题答案分布图' % question['q_number'],
                'stat': [
                    {'name': studentAnswer, 'y': 1},
                ]
            }
        else:
            # 更新qStat
            new = True
            for statItem in qStat['stat']:
                if studentAnswer == statItem['name']:
                    statItem['y'] += 1
                    new = False
                    break
            if new:
                qStat['stat'].append({'name': studentAnswer, 'y': 1})
        # 保存qStat
        self.saveStat(qStatPath, qStat)
