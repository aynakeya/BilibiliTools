Bilibili Audio DownLoader<br>
bilibili音乐站下载器<br>
<br>
一个可以下载bilibili音乐站歌单以及歌曲的小工具<br>
利用了类console的模式，操作简单<br>
<br>
使用方法<br>
`python3 BilibiliAudioGet.py`<br>
命令<br>
audio : download a audio file(s) by enter url 下载歌曲<br>
playlist : download a playlist 下载歌单<br>
user : playlist : download all the song of a user 下载up主的所有歌曲<br>
help : show help 显示帮助<br>
quit : Quit 退出<br>
参数<br>
-l/--lyric : download lyric (If have) 下载歌词<br>
-q : choose the song quality from 0 to 2, higher the value, higher the quality (if you want) 选择音质0-128k,1-192k,3-320k<br>
--disable-audio : do not download audio 不下载音乐<br>
<br>
Exmaple<br>

```
// 下载歌单
playlist https://www.bilibili.com/audio/am84371
// 下载up主所有的歌曲
user https://space.bilibili.com/2932528/audio
// 下载歌曲
audio https://www.bilibili.com/audio/au282881
// 下载多个歌曲
audio https://www.bilibili.com/audio/au282881 https://www.bilibili.com/audio/au18076
```
<br>
<br>
Csharp 版<br>
所需环境: .NET Framework 4.5<br>
直接运行就完事了<br>

<br>
Jan.18.2019 : Fisrt Upload.<br>
Jan.20.2019 : Add CSharp Version<br>
Jan.20.2019 : Change api, support quality choose<br>
May.25.2019 : Fix bug in CSharp<br>