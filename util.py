# coding:utf8
# author:winton

import codecs
import json


class Util:
    @staticmethod
    def loadJsonFile(jsonFile):
        f = codecs.open(jsonFile, encoding='utf-8')
        return json.loads(f.read())
