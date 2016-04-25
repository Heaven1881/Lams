# coding:utf8
# author: winton

import sys
import getopt
import json
import logging
import os
import base64


class ConsumerRunner:
    def __init__(self, classInfo):
        self.moduleName = classInfo['moduleName']
        self.className = classInfo['className']
        self.dataDir = classInfo['dataDir']

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            filename='/home/winton/git/Lams/log/csm.%s.log' % self.className,
            encoding='utf8'
        )

        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)
        module = __import__(self.moduleName, fromlist=[self.className])
        Csm = getattr(module, self.className)
        self.csm = Csm(self.dataDir)

    def do(self, event):
        try:
            self.csm.doEvent(event)
        except Exception as e:
            logging.exception('%s - %s' % (str(e), self.className))


if __name__ == '__main__':
    oplist, args = getopt.getopt(sys.argv[1:], 'm:c:e:d:')
    for o, a in oplist:
        if o == '-m':
            moduleName = a
        elif o == '-c':
            className = a
        elif o == '-e':
            event = a
        elif o == '-d':
            dataDir = a
        else:
            assert False, 'unkown option "%s"' % o
    cr = ConsumerRunner({
        'moduleName': moduleName,
        'className': className,
        'dataDir': dataDir
    })
    cr.do(json.loads(base64.b64decode(event)))
