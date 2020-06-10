# BilibiliTools


**Bilibili 工具箱**

这里上传了我自己写的b站小工具 (大部分都是我自己要用的)

欢迎各位的 star 和 fork.

---
## Introduction

*old 是重写前的版本*

- config.py: 配置文件 非常重要！！！！
- biliget: bilibili聚合下载器
- biliFavExtractor.py: 收藏夹信息导出

---
### config.py

**配置文件**

```python
class Config:
	# http代理列表 尚未完工
    proxies = {}
	# 通用http头，不建议修改
    commonHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }
	# bilibili的cookie，用于下载高清视频，自己填进去
    commonCookies = {
                     "SESSDATA":"",
    }
	# 默认下载路径，自己修改
    saveroute = r"C:\Download\bilidown"
	
	# aria的rpc地址，默认是这个
    aria2rpc = "http://localhost:6800/rpc"
    #if no token provide, using None 如果有密匙，填密匙，没有就填None
    aria2token = None
	
	# 默认下载器，默认使用requests
    defaultDownloader = "requests"
	
	# 可使用的下载器
    # Available: aria2, requests
    useDownloader = {"aria2":True,
                     "requests":True}
	
	# 可使用的模块，目前只有一个音乐文件tag编辑器，还没有完全做好
    # useModules  = ["infoEditor"]
	
	# 默认下载质量
    defaultQuality = 116
```


---
### biliget.py

**console 版本的bilibili聚合下载器**

支持视频，封面，收藏夹，音乐，歌词，音乐封面.

支持下载番剧.

支持aria2,以及原生python下载.

*(你说的不是you-get嘛？)*
*当然不是，you-get 1mb不到的下载速度有个鸡儿用。还一次只能下载一个视频。*
*本程序支持aria2下载，跑满带宽，巨鸡儿牛皮。*
*（演示视频呢）*
*被pilipili退回了。*

---
### biliFavExtractor.py

**收藏夹信息导出**

到处收藏夹里的信息为 csv 文件

默认保存路径是config.py 里的saveroute

食用方法

python biliFavExtracter.py [options] favlink

Options:

-h/--help: show help

-s/--saveroute=: saveroute

-n/--number=: number you want to export(default: 1)


---
## 更新日记 Change Log:

2019/11/20: 开始重写