import requests
import time
import json

'''
{"code":0,"message":"0","ttl":1} 收藏成功
{"code":11007,"message":"你已经收藏过该视频！","ttl":1} 已收藏
{"code":-111,"message":"csrf 校验失败","ttl":1} csrf 校验失败
{"code":10003,"message":"不存在该稿件","ttl":1} 不存在该稿件
{"code":-503,"message":"调用速度过快","ttl":1} 调用速度过快
{"code":-404,"message":"啥都木有","ttl":1} 啥都没有
{"code":-101,"message":"账号未登录","ttl":1} 账号未登录
'''

codes = {'0':(0,'收藏成功'),
         '11007':(0,"你已经收藏过该视频！"),
         '10003':(1,"不存在该稿件"),
         '-404':(1,"啥都木有"),
         '-503':(2,"调用速度过快"),
         '-111':(-1,"csrf 校验失败"),
         '-101':(-1,"账号未登录,可能是cookie过期")}

raw_cookie = input("Enter cookie: ")
bilicookie = {}
for line in raw_cookie.split(';'):
    key,value = line.split('=')
    if key[0] == ' ':
        key = key[1::]
    bilicookie[key] = value
csrf = bilicookie['bili_jct']
fid = input("Enter fid: ")
aid = input("Enter avs: ").split(" ")

print("共%s个视频，开始尝试添加。" % len(aid))

url = 'https://api.bilibili.com/x/v2/fav/video/add'
headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
           'Host':'api.bilibili.com',
           'Origin':'https://www.bilibili.com',
           }
data = {'aid': '','fid': fid,'jsonp': 'jsonp','csrf': csrf}


def addfav(av):
    data['aid'] = av
    resp = requests.post(url, headers=headers, cookies=bilicookie, data=data)
    msg = json.loads(resp.content.decode('utf-8'))
    code = str(msg["code"])
    return code,msg

if __name__=="__main__":
    avnotexsit = []
    for av in aid:
        '''
        data['aid'] = av
        resp = requests.post(url, headers=headers, cookies=bilicookie, data=data)
        msg = resp.content.decode('utf-8')
        code = msg[msg.find('"code":')+7:msg.find(',"message"'):]
        '''
        code, msg = addfav(av)
        if len(code) >6 or len(code) < 1:
            while len(code) >10 or len(code) < 1:
                print("Get Code Error")
                print("Sleep for 3 sec")
                time.sleep(3)
                code, msg = addfav(av)
        if code in codes:
            pattern, msg = codes[code]
            print("尝试第%s个，添加视频av%s到收藏夹%s---返回信息:%s(code:%s)" % (aid.index(av)+1,av, fid, msg, code))
            if pattern == 1:
                avnotexsit.append(av)
            if pattern == 2:
                while pattern == 2:
                    print("Sleep for 3 sec")
                    time.sleep(3)
                    code, msg = addfav(av)
                    pattern, msg = codes[code]
                    print("重试第%s个，添加视频av%s到收藏夹%s---返回信息:%s(code:%s)" % (aid.index(av)+1,av, fid, msg, code))
            if pattern == -1:
                print("please re try!")
                break
        else:
            print("Unexceppt Error: %s:" % msg)

    if len(avnotexsit) > 0:
        print("不存在的av号:\n%s" % avnotexsit)

    print("Finished")

'''
resp = requests.post(url,headers = headers,cookies = bilicookie,data=data)
print(resp.content.decode('utf-8'))
'''