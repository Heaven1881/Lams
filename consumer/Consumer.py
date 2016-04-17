# coding:utf8
# author: winton

import logging
import codecs
import datetime
import json
import os


class Consumer:
    def __init__(self, dataDir):
        self.dataDir = dataDir

    def doEvent(self, event):
        if event is not None:
            try:
                self.run(event, self.dataDir)
            except Exception as e:
                logging.exception(str(e))
        else:
            logging.warning('NoneObject event')

    def run(self, event, dataDir):
        logging.warning('undefine run function')

    def loadStat(self, filepath):
        return self.loadJsonFromFile(filepath)

    def loadJsonFromFile(self, filepath):
        if not os.path.exists(os.path.join(self.dataDir, filepath)):
            return None
        f = codecs.open(os.path.join(self.dataDir, filepath), encoding='utf8')
        jsonStr = f.read()
        if jsonStr:
            return json.loads(jsonStr)
        else:
            return None

    def saveStat(self, filepath, jsonData):
        # 更新lastMdf
        t = datetime.datetime.now()
        createtime = t.strftime('%Y-%m-%d:%H:%M:%S')
        jsonData['lastMdf'] = createtime
        # 相关信息赋值
        jsonData['type'] = self.typeStr
        jsonData['visualization'] = self.visualization

        self.saveJsonToFile(filepath, jsonData)

    def saveJsonToFile(self, filepath, jsonData):
        filepath = os.path.join(self.dataDir, filepath)
        fileDir, filename = os.path.split(filepath)
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        f = codecs.open(filepath, 'w', 'utf8')
        try:
            f.write(json.dumps(jsonData, ensure_ascii=False, separators=(',', ':')))
        finally:
            f.close()

    def updateJsonInList(self, listObj, jsonObj, primaryKey='name'):
        '''
        在listObj中插入jsonObj，如果不存在则新建，如果已经存在则覆盖，根据primaryKey判断是否存在
        '''
        found = False
        for item in listObj:
            if item[primaryKey] == jsonObj[primaryKey]:
                found = True
                item.update(jsonObj)
                break
        if not found:
            listObj.append(jsonObj)

    def getJsonInList(self, listObj, key, primaryKey='name'):
        for item in listObj:
            if item[primaryKey] == key:
                return item
        return None

    def genStatFromDetail(self, details, genKey=['name', 'y'], keyName=['name', 'y']):
        '''
        根据detail生成stat
        '''
        if len(genKey) != len(keyName):
            logging.error('length mismatch')
            return
        stat = []
        for item in details:
            appendItem = {}
            for i in range(len(keyName)):
                appendItem[keyName[i]] = item[genKey[i]]
            stat.append(appendItem)
        return stat
