# coding: utf8
# author: winton

import argparse
import logging
import codecs
import json
import os


class GradeProducer:
    statedNo = [
        30240243,  # 操作系统
        40240692,  # 存储技术基础
        40240392,  # 多媒体技术基础及应用
        40240532,  # 机器学习概论
        40240422,  # 计算机图形学基础
        40240882,  # 计算机网络专题训练
        40240443,  # 计算机系统结构
        30240422,  # 数据库专题训练
        40240492,  # 数据挖掘
        10420854,  # 数学实验
        20240033,  # 数值分析
        40240062,  # 数字图像处理
        40240762,  # 搜索引擎技术基础
        41120022,  # 网络编程技术
        40240013,  # 系统分析与控制
        40240892,  # 现代密码学
        40240702,  # 以服务为中心的软件开发设计与实现
    ]

    def __init__(self, inputFilename, outputDir):
        self.inputFilename = inputFilename
        self.outputDir = outputDir

    def loadJsonFromFile(self, filepath):
        if not os.path.exists(filepath):
            logging.warning('loading a file not exists [path=%s]' % filepath)
            return None
        f = codecs.open(filepath, encoding='utf8')
        jsonStr = f.read()
        f.close()
        if jsonStr:
            return json.loads(jsonStr)
        else:
            logging.warning('read None content')
            return None

    def saveJsonToFile(self, filepath, event):
        f = codecs.open(filepath, 'w', 'utf8')
        try:
            f.write(json.dumps(event, ensure_ascii=False, indent=4, separators=(',', ':')))
        finally:
            f.close()

    def run(self):
        data = self.loadJsonFromFile(self.inputFilename)
        for cInfo in data['result']:
            if cInfo['cNo'] in self.statedNo:
                statData = {
                    'visualization': 'areaspline',
                    'type': 'CountStat',
                    'title': u'%s 成绩分布' % cInfo['cName'],
                    'enrolled': 0,
                    'cName': cInfo['cName'],
                    'detail': [
                        {
                            'name': '%d<=x<%d' % (t, t + 10),
                            'low': t,
                            'count': 0,
                        } for t in range(0, 101, 10)
                    ],
                    'stat': [],
                }
                for gradeInfo in cInfo['info']:
                    grade = gradeInfo['grade']
                    for detailItem in statData['detail']:
                        low = detailItem['low']
                        high = low + 10
                        if grade >= low and grade < high:
                            detailItem['count'] += 1
                    statData['enrolled'] += 1
                # TODO 处理stat
                for detailItem in statData['detail']:
                    statData['stat'].append({
                        'name': detailItem['name'],
                        'y': 1.0 * detailItem['count'] / statData['enrolled'],
                    })
                self.saveJsonToFile(os.path.join(self.outputDir, '%d.json' % cInfo['cNo']), statData)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='parser json data')
    ap.add_argument('-i', help='input filename')
    ap.add_argument('-o', help='output dir')
    args = ap.parse_args()

    out = '/home/winton/git/Lams/var/data.other'

    if args.i is None:
        print 'no input or output'
        exit(0)
    instance = GradeProducer(args.i, out)
    instance.run()
