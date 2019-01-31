from optparse import OptionParser
import re
from threading import Lock
import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

msgList=[]
isSaveToFile=False
threadNum=20
useragen="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
msgLock=Lock()

def saveFile(fileName):
    file=open(fileName,'w')
    for i in msgList:
        file.write(i+"\n")
    file.flush()
    file.close()


def help():
    print('''
python3 GetIPLocation.py -i [targetIP] -o [saveFile];
python3 GetIPLocation.py -f [targetIPs] -o [saveFile];
 ''')
    exit(-1)

# 获取输入参数
def _get_args():
    parser = OptionParser(usage="usage: %prog [options] args")
    parser.add_option("-i", "--ip", help="Target IP", dest='ip')
    parser.add_option("-f", "--file", help="Target File", dest='targetFile')
    parser.add_option("-o", "--output", help="Save to file",dest="output")
    opts, args = parser.parse_args()
    return opts

def doSingle(ip):
    global msgList
    global msgLock
    temp = re.match(r'((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d))', ip,
                    re.M | re.I)
    if temp != None:
        url="http://www.ip38.com/ip.php?ip="+str(ip)
        req=requests.get(url=url,headers={"User-Agen":useragen}).text
        bs=BeautifulSoup(req,"html.parser")
        try:
            ul=bs.select("font[color='#FF0000']")[2]
        except:
            return None
        ipStr=ip+"\t"+str(ul.string)
        with msgLock:
            msgList.append(ipStr)
        print(ipStr)
    else:
        return None


def doFile(file):
    try:
        file=open(file,'r')
        file=file.readlines()
    except:
        print("No such file!")
        return
    ips=[]
    for i in file:
        ips.append(i.split("\n")[0])
    try:
        pool = ThreadPool(processes=threadNum)
        result = pool.map_async(doSingle, ips).get(999999)
        pool.close()
        pool.join()
        return result
    except KeyboardInterrupt:
        print("Aready to exit!")



def main():
    ip=None
    targets=None
    out=None
    try:
        opts = _get_args()
        ip = opts.ip
        targets= opts.targetFile
        out=opts.output
    except Exception as e:
        print(e)
    if ip==None and targets==None:
        help()
    if not ip is None:
        doSingle(ip)
    if not targets is None:
        doFile(targets)
    if not out is None:
        saveFile(out)

if __name__ == "__main__":
    main()




