# coding:utf8
# author:winton

import datetime
import logging

from Consumer import Consumer


class PiazzaActionCsm(Consumer):
    '''
    收集和处理从piazza平台上获取的信息
    收集平台上学生进行各项活动的次数统计
    '''
    typeStr = 'CountStat'
    visualization = 'column'

    def statKey(self, users, key, step=10, n=10, min=0):
        logging.info('stat "%s"' % key)
        iStat = {
            'min': min,
            'max': min + step * n - 1,
            'stat': [{'name': '%d~%d' % (t, t + step - 1), 'y': 0} for t in range(min, min + n * step, step)]
        }
        for u in users:
            count = int(u[key])
            if count < iStat['min']:
                logging.warning('unexcepted value %d [u=%s]' % (count, u))
            if count > iStat['max']:
                extend = (count - iStat['max']) / step + 1
                iStat['stat'] += [{'name': '%d~%d' % (t, t + step - 1), 'y': 0} for t in range(iStat['max'] + 1, iStat['max'] + extend * step, step)]
                iStat['max'] += extend * step
                logging.info('extend stat, now max = %d' % iStat['max'])
            index = count / step
            try:
                iStat['stat'][index]['y'] += 1
            except:
                logging.info('index = %d, count=%d, iStat_max=%d, group=%d, extend=%s' % (index, count, iStat['max'], len(iStat['stat']), count > iStat['max']))
                raise Exception('debug')
        return iStat

    def run(self, event, dataDir):
        userStat = event['content']['users']
        asksStat = self.loadStat('asks.json')
        # 判断这条信息是否最新，如果不是最新，则不处理
        if asksStat is not None:
            eventTime = datetime.datetime.strptime(event['time'], '%Y-%m-%d:%H:%M:%S')
            lastTime = datetime.datetime.strptime(asksStat['eventTime'], '%Y-%m-%d:%H:%M:%S')
            if lastTime > eventTime:
                logging.info('skip past event [eventTime=%s] [lastTime=%s]' % (event['time'], asksStat['eventTime']))
                return
        else:
            logging.info('no past data, consumer will handle current data')
        # TODO 调用statKey解析数据并分别储存
        # 重写所有信息
        eventTime = datetime.datetime.now()
        eventTime = eventTime.strftime('%Y-%m-%d:%H:%M:%S')

        asksStatPre = self.statKey(userStat, 'asks', step=2)
        asksStat = {
            'title': u'piazza平台提问情况',
            'xTitle': u'分布',
            'yTitle': u'人数',
            'stat': asksStatPre['stat'],
            'eventTime': eventTime,
        }
        self.saveStat('asks.json', asksStat)

        viewsStatPre = self.statKey(userStat, 'views')
        viewsStat = {
            'title': u'piazza平台浏览情况',
            'xTitle': u'分布',
            'yTitle': u'人数',
            'stat': viewsStatPre['stat'],
            'eventTime': eventTime,
        }
        self.saveStat('views.json', viewsStat)

        postsStatPre = self.statKey(userStat, 'posts')
        postsStat = {
            'title': u'piazza平台发帖情况',
            'xTitle': u'分布',
            'yTitle': u'人数',
            'stat': postsStatPre['stat'],
            'eventTime': eventTime,
        }
        self.saveStat('posts.json', postsStat)

        daysStatPre = self.statKey(userStat, 'days')
        daysStat = {
            'title': u'piazza平台在线天数分布情况',
            'xTitle': u'分布',
            'yTitle': u'人数',
            'stat': daysStatPre['stat'],
            'eventTime': eventTime,
        }
        self.saveStat('days.json', daysStat)

        answersStatPre = self.statKey(userStat, 'answers')
        answersStat = {
            'title': u'piazza平台回答情况',
            'xTitle': u'分布',
            'yTitle': u'人数',
            'stat': answersStatPre['stat'],
            'eventTime': eventTime,
        }
        self.saveStat('answers.json', answersStat)
