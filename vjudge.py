import requests
from bs4 import BeautifulSoup
from urllib import parse
import json, re, random
from multiprocessing.dummy import Pool as ThreadPool

BASE = 'https://cn.vjudge.net'
UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
TimeOut = 5
FNAME = 'today-problem' # 输出文件名

def login(S, username, password):
    login_url = BASE + '/user/login'
    login_payload = {
        'username': username,
        'password': password
    }
    login_headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': BASE,
        'referer': BASE + '/',
        'user-agent': UserAgent,
        'x-requested-with': 'XMLHttpRequest'
    }
    r1 = S.post(url=login_url, headers=login_headers, data=parse.urlencode(login_payload), timeout=TimeOut)
    if not r1.ok:
        print('login error')

# 返回一个prob字典
def getprob(S, url):
    probdict = {}
    # article
    getarticle_url = url
    getarticle_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'referer': BASE + '/article',
        'upgrade-insecure-requests': '1',
        'user-agent': UserAgent
    }
    r2 = S.get(url=getarticle_url, headers=getarticle_headers, timeout=TimeOut)
    if not r2.ok:
        print('getarticle error')
        return {}
    # print(r2.url)

    soup = BeautifulSoup(r2.text, features="html.parser")
    probdata = json.loads(soup.find(attrs={'name': 'dataJson'}).text)
    probcontent = probdata['content']
    problist = re.findall('\[problem.*?\]', probcontent)
    # print(len(problist))

    # solveInfo
    solveinfo_probkey = parse.quote('probs[]')
    solveinfo_arr = []
    for i in problist:
        s = i.split(':')[1][:-1]
        s = s.strip().replace(' ', '-')
        solveinfo_arr.append(solveinfo_probkey + '=' + s)
        probdict[s] = False

    solveinfo_payload = '&'.join(solveinfo_arr)

    solveinfo_url = BASE + '/status/solveInfo'
    solveinfo_headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': BASE,
        'referer': getarticle_url,
        'user-agent': UserAgent,
        'x-requested-with': 'XMLHttpRequest'
    }
    r3 = S.post(url=solveinfo_url, headers=solveinfo_headers, data=solveinfo_payload, timeout=TimeOut)
    if not r3.ok:
        # print(len(solveinfo_payload), solveinfo_payload[:100])
        print(S.cookies)
        print('solveinfo error')
        return {}

    probdict.update(r3.json())
    return probdict

def logout(S):
    logout_url = BASE + '/user/logout'
    logout_headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'dnt': '1',
        'origin': BASE,
        'referer': BASE + '/',
        'user-agent': UserAgent,
        'x-requested-with': 'XMLHttpRequest'
    }
    r4 = S.post(url=logout_url, headers=logout_headers)
    if not r4.ok:
        print('logout error')

def run(username, password, articlelist, probnum):
    # 获取题目
    S = requests.Session()
    login(S, username, password)
    probdict = {}
    for i in articlelist: # 遍历即可 减轻vj的压力
        a = getprob(S, i)
        probdict.update(a)

    logout(S)
    S.close()
    # 输出
    problist = [k for k, v in probdict.items() if not v] # 过滤出没AC的题目
    random.shuffle(problist)
    finalproblist = problist[ : probnum]
    with open(FNAME + '.html', 'w') as f:
        f.write('<html><head><title>Today ProblemSet (๑•̀ㅂ•́)و✧</title></head><body>')
        for i in finalproblist:
            f.write('<a  target="_blank" href="' + BASE + '/problem/' + i + '">'+ i +'</a><br>')
        f.write('</body></html>')

if __name__ == '__main__':
    username = 'XXXXX'
    password = 'XXXXXXXXX'
    articlelist = [
        'https://cn.vjudge.net/article/775',
        'https://vjudge.net/article/752'
    ]
    problemnum = 100
    run(username, password, articlelist, problemnum)
