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


class SectionScoreConsumer(Consumer):
    '''
    统计学生每个章节的分数，以及所有人的平均分
    '''
    typeStr = 'CountStat'
    visualization = 'polar'
    sectionDef = {
        'Section-0': [1197, 1198, 1199, 1120],
        'Section-1': [1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162],
        'Section-2': [1191, 1192, 1193, 1194, 1196, 1195, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1173, 1172, 1174, 1175],
        'Section-3': [1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219],
        'Section-4': [],
        'Section-5': [1286, 1287, 1288, 1289, 1290, 1291],
        'Section-6': [1307, 1308, 1309, 1310, 1334],
        'Section-7': [1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327],
        'Section-8': [],
        'Section-9': [1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350],
        'Section-10': [1367, 1368, 1369, 1370, 1371],
        'Section-11': [1405, 1406, 1407, 1408, 1409, 1410, 1411],
        'Section-12': [1428, 1429, 1430, 1431],
        'Section-13': [],
        'Section-14': [],
        'Section-15': [1436, 1437, 1438, 1439, 1440, 1441],
        'Section-16': [],
        'Section-17': [1447, 1448, 1449, 1450, 1451, 1452],
        'Section-18': [1453, 1454, 1455, 1456, 1457, 1458],
        'Section-19': [1459, 1460, 1461],
        'Section-20': [1462, 1463, 1464, 1465, 1466, 1467, 1468],
        'Section-21': [1469, 1470, 1471, 1472, 1473, 1474, 1475],
        'Section-22': [1476, 1477, 1478, 1479, 1480],
        'Section-23': [1481, 1482, 1483, 1484, 1485, 1486, 1487]
    }

    def getScectionName(self, qno):
        for sectionName in self.sectionDef:
            qnos = self.sectionDef[sectionName]
            if qno in qnos:
                return sectionName
        return 'Other'

    def run(self, event, dataDir):
        student = event['related']['student']
        question = event['related']['question']
        sectionName = self.getScectionName(question['q_number'])
        score = event['content']['score']

        statPath = '%s.sections.stat.json' % student['email']
        avgStatPath = 'all.sections.stat.json'

        # 读取并更新stat
        stat = self.loadStat(statPath)
        if stat is None:
            logging.info('create new stat file [path=%s]' % statPath)
            stat = {
                'title': u'%s每讲得分' % student['email'],
                'stated': [question['q_number']],
                'stat': [
                    {'name': sectionName, 'y': score}
                ],
            }
        elif question['q_number'] in stat['stated']:
            # 目前没有想到更好的实现方法
            logging.info('skiped event because question [%s] has been stated' % question['q_number'])
            return
        else:
            stat['stated'].append(int(question['q_number']))
            createNew = True
            for statItem in stat['stat']:
                if statItem['name'] == sectionName:
                    createNew = False
                    statItem['y'] += score
                    break
            if createNew:
                stat['stat'].append({'name': sectionName, 'y': score})
        self.saveStat(statPath, stat)

        # 读取并更新avgStat
        avgStat = self.loadStat(avgStatPath)
        if avgStat is None:
            logging.info('create new stat file [path=%s]' % avgStatPath)
            avgStat = {
                'title': u'课程平均每讲得分',
                'detail': [
                    {'name': section, 'student': 0, 'totalScore': 0, 'stated': []} for section in self.sectionDef
                ],
                'stat': [
                    {'name': section, 'y': 0} for section in self.sectionDef
                ],
            }
        # 更新数据信息
        createNewDetail = True
        for detailItem in avgStat['detail']:
            if detailItem['name'] == sectionName:
                if student['email'] not in detailItem['stated']:
                    detailItem['student'] += 1
                    detailItem['stated'].append(student['email'])
                detailItem['totalScore'] += score
                createNewDetail = False
                break
        if createNewDetail:
            avgStat['detail'].append({'name': sectionName, 'student': 1, 'totalScore': score, 'stated': [student['email']]})
        # 更新统计信息
        avgStat['stat'] = []
        for detailItem in avgStat['detail']:
            if detailItem['student'] == 0:
                avgStat['stat'].append({'name': detailItem['name'], 'y': 0.0})
            else:
                avgStat['stat'].append({'name': detailItem['name'], 'y': 1.0*detailItem['totalScore']/detailItem['student']})
        self.saveStat(avgStatPath, avgStat)
