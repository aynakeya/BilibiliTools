# BilibiliTools


**Bilibili 工具箱(划掉)**

这里上传了我自己写的b站小工具 (大部分都是我自己要用的)

欢迎各位的 star 和 fork.

---
## Introduction

- config.py: 配置文件 非常重要！！！！
- biliget: 聚合下载器

---
### biliget.py

**console 版本的聚合下载器**

已完全重构

重构

现在由几步构成

1. downloader 下载器
2. modules 命令模组
3. sources 下载源

具体如下

biliget 会读取需要加载的module, module里使用SourceSelector选择对应的source

在获取BaseSource后调用download进行下载。

支持bilibili视频，封面，收藏夹，音乐，歌词，音乐封面.

支持下载番剧.

支持wenku8, 樱花动漫，卡卡动漫

支持aria2,以及原生python下载.

*(你说的不是you-get嘛？)*
*当然不是，you-get 1mb不到的下载速度有个鸡儿用。还一次只能下载一个视频。*
*本程序支持aria2下载，跑满带宽，巨鸡儿牛皮。*
*（演示视频呢）*
*被pilipili退回了。*

---
### JSCripts

**js脚本**

用于全平台浏览器的收藏夹脚本

具体使用方式就是加入收藏夹，然后把地址改为js代码

videoDownload - 视频下载

videoCover - 封面下载


---
### biliget-gui pyinstaller build

Make spec file

```
// one file 
pyi-makespec --onefile --windowed --add-data "config.json;." --add-data "cookies;cookies" --add-binary "mpv-1.dll;." biliget-gui.py
// one folder
pyi-makespec --windowed --add-data "config.json;." --add-data "cookies;cookies" --add-binary "mpv-1.dll;." biliget-gui.py

pyinstaller biliget-gui.spec
```

Or just build

```
// one file 
pyinstaller --onefile --windowed --add-data "config.json;." --add-data "cookies;cookies" --add-binary "mpv-1.dll;." biliget-gui.py
// one folder
pyinstaller --windowed --add-data "config.json;." --add-data "cookies;cookies" --add-binary "mpv-1.dll;." biliget-gui.py
```

---
## 更新日记 Change Log:

2019/11/20: 开始重写

2020/06/10: 重写完成