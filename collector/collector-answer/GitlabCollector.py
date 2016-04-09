# coding:utf8
# author:winton

import logging
import os
import base64
import time
import httplib
import json
import subprocess

from collector import Colllector


class GitlabCollector(Colllector):
    '''
    和gitlab相关的收集者，可以保存上一次的记录，支持增量处理
    '''
    def __init__(self, datapool, gitConfig):
        Colllector.__init__(self, datapool)
        self.hostname = gitConfig['hostname']
        self.port = gitConfig['port']

        self.repoId = gitConfig['repo_id']
        self.rootToken = gitConfig['root_token']
        self.ref = gitConfig['ref']
        self.headers = {}

        self.localRepo = gitConfig['localRepo']

    def loadJsonFromRemoteRepo(self, filepath):
        '''
        从gitlab的指定路径下读取文件，如果文件不存在，返回None
        '''
        url = '/api/v3/projects/%(repo_id)d/repository/files?private_token=%(root_token)s&&file_path=%(filepath)s&&ref=%(ref)s' % {
            'repo_id': self.repoId,
            'root_token': self.rootToken,
            'filepath': filepath,
            'ref': self.ref
        }
        conn = httplib.HTTPConnection(self.hostname, self.port, timeout=30)
        content = None
        try:
            conn.request("GET", url, None, self.headers)
            response = conn.getresponse()
            if response.status == 200:
                response_data = response.read()
                response_data = json.loads(response_data)
                content = json.loads(base64.b64decode(response_data["content"]))
            elif response.status == 404:
                pass
            else:
                msg = json.loads(response.read())['message']
                logging.info('readContent: wrong status returned [msg=%s] [filepath=%s]' % (msg, filepath))
        except httplib.HTTPException as e:
            logging.warning('Exception when get file from remote repo [%s]' % str(e))
        finally:
            conn.close()
        return content

    def loadJsonFromLocalRepo(self, filepath):
        filepath = os.path.join(self.localRepo, filepath)
        logging.debug('loading flie in "%s"' % filepath)
        jsonData = self.loadJsonFromFile(filepath)
        return jsonData

    def recodeLastCommit(self):
        # 保存上一次的数据
        newfile = 'last/last_commit.%d.json' % int(time.time())
        cmd = 'mv last/last_commit.json %s' % newfile
        ret = subprocess.call(cmd, shell=True)
        if ret == 0:
            logging.info('save last_commit.json to %s' % newfile)
        # 读取新数据
        cmd = 'git log | head -n 1| awk \'{print $2}\''
        commitId = subprocess.check_output(cmd, shell=True, cwd=self.localRepo)
        logging.info('init last commit [id=%s]' % commitId.strip())
        self.saveJsonToFile('last/last_commit.json', {'id': commitId.strip()})

    def readLastCommit(self):
        '''
        读取新的commit id
        '''
        cmd = 'git log | head -n 1| awk \'{print $2}\''
        commitId = subprocess.check_output(cmd, shell=True, cwd=self.localRepo)
        return commitId.strip()

    def getLastestConmit(self, perPage=100, page=0):
        '''
        调用api获取最近的记录
        注意，这个方式需要网络访问
        '''
        url = '/api/v3/projects/%(repo_id)d/repository/commits?private_token=%(root_token)s&&ref_name=%(ref)s&&page=%(page)d&&per_page=%(per_page)d' % {
            'repo_id': self.repoId,
            'root_token': self.rootToken,
            'ref': self.ref,
            'per_page': perPage,
            'page': page,
        }
        logging.debug(url)
        conn = httplib.HTTPConnection(self.hostname, self.port, timeout=30)
        commitsInfo = None
        try:
            conn.request('GET', url, None, self.headers)
            response = conn.getresponse()
            if response.status == 200:
                response_data = response.read()
                commitsInfo = json.loads(response_data)
            else:
                msg = json.loads(response.read())['message']
                logging.warning('wrong status when reading lastest commits [status=%d] [msg=%s]' % (response.status, msg))
        except httplib.HTTPException as e:
            logging.warning('Exception when get file from remote repo [%s]' % str(e))
        finally:
            conn.close()
        return commitsInfo

    def updateLoaclRepo(self):
        cmd = 'git pull'
        # TODO git pull 需要密码来工作
        output = subprocess.check_output(cmd, shell=True, cwd=self.localRepo)
        logging.debug(output)
        return output

    def getModifiedFilesAfterLastCommit(self):
        '''
        从本地库获取上次commit以后更改的所有文件列表
        '''
        # 获取上次收集记录的last_commit,如果last_commit不存在,则返回使用库中的最新commit作为last_commit
        lastCommitInfo = self.loadLastCommit()
        if not lastCommitInfo:
            self.recodeLastCommit()
            lastCommitInfo = self.loadLastCommit()
        if not lastCommitInfo:
            logging.warning('lastCommit not found, function returning...')
            raise Exception('lastCommit not found!')
        lastCommit = lastCommitInfo['id']
        logging.info('lastCommit [%s]' % lastCommit)

        # 获取库中最新的commit并保存
        headCommit = self.readLastCommit()
        logging.info('headCommit [%s]' % headCommit)

        cmd = 'git diff %s %s --name-only' % (lastCommit, headCommit)
        logging.debug('cmd [%s]' % cmd)
        modfiedListStr = subprocess.check_output(cmd, shell=True, cwd=self.localRepo)
        logging.debug(modfiedListStr.strip().split('\n'))
        return modfiedListStr.split('\n') if modfiedListStr.strip() else []

    def getCommitsAfterLastCommit(self, perPage=100, page=0):
        '''
        递归查询,获取上次commit以后的所有记录
        注意：这个函数需要访问网络，同时实现方式并不优雅，建议使用函数getModifiedFilesAfterLastCommit
        '''
        lastCommit = self.loadLastCommit()
        if not lastCommit:
            self.recodeLastCommit()
            lastCommit = self.loadLastCommit()
        if not lastCommit:
            logging.warning('lastCommit not found, function returning...')
            raise Exception('lastCommit not found!')
        commitsInfo = self.getLastestConmit(perPage, page)
        lastCommitId = lastCommit['id']
        index = 0
        for commit in commitsInfo:
            index += 1
            if lastCommitId == commit['id']:
                logging.info('find last commit at index(%d), returning...' % index)
                return commitsInfo[:index-1]
        # 如果没有找到，就读取下一页继续找
        logging.info('didnt found, load next %d commits...' % perPage)
        return commitsInfo + self.getCommitsAfterLastCommit(perPage, page + 1)

    def saveLastCommit(self, commit):
        self.saveJsonToFile('last/last_commit.json', commit)

    def loadLastCommit(self):
        return self.loadJsonFromFile('last/last_commit.json')

    # TODO 处于对这个类的完整性考虑，需要实现一个读取每一条commit记录对应的文件的方法
    # 但是由于目前暂时不需要，所以暂不实现
