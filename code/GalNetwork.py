import GalError
import requests
import subprocess
import re

GET = "GET"
POST = "POST"

def connect(url):
    return Web(url)


class Web:
    def __init__(self, url):
        self.url = url

        self.domain = url.split("//")[1].split("/")[0]
        self.protocol = 'http' if not url[4] == 's' else 'https'
        
    def getPing(self):
        '''Return(ip,丢包率,最短，最长，平均)'''
        domain = self.domain
        p = subprocess.Popen(["ping.exe", domain], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        out = p.stdout.read().decode('gbk')
        print(out)
        regIP = r'\[\d+\.\d+\.\d+\.\d+\]'
        regLost = r'\(\d+%'
        regMinimum = u'Minimum = \d+ms|最短 = \d+ms'
        regMaximum = u'Maximum = \d+ms|最长 = \d+ms'
        regAverage = u'Average = \d+ms|平均 = \d+ms'
        ip = re.search(regIP, out)
        lost = re.search(regLost, out)
        minimum = re.search(regMinimum, out)
        maximum = re.search(regMaximum, out)
        average = re.search(regAverage, out)
        if ip:
            ip = ip.group()[1:-1]
        if lost:
            lost = lost.group()[1:]
        if minimum:
            minimum = ''.join(list(filter(lambda x:x.isdigit(),minimum.group())))
        if maximum:
            maximum = ''.join(list(filter(lambda x:x.isdigit(),maximum.group())))
        if average:
            average = ''.join(list(filter(lambda x:x.isdigit(),average.group())))
        return (ip,lost,minimum,maximum,average)

    def getContent(self, method=GET, args=None):
        ctx = requests.get(self.protocol+"://"+self.domain, args) if method == GET else None
        return ctx.content
