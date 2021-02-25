import m3u8,glob,os,subprocess
import re
def m3u8Extract(url):
    try:
        m3u8obj = m3u8.load(url)
        if len(m3u8obj.playlists) != 0:
            return m3u8Extract(m3u8obj.playlists[0].base_uri+m3u8obj.playlists[0].uri)
        return [seg.base_uri+seg.uri for seg in m3u8obj.segments]
    except:
        print("m3u8 extract fail")
        return []

def m3u8Combine(route):
    target_file = os.path.join(os.path.dirname(route),
                               os.path.basename(route)+".ts")
    with open(target_file,"wb") as tf:
        for path in glob.glob(os.path.join(route, "*.ts")):
            with open(path, "rb") as f:
                tf.write(f.read())

def m3u8FFmpegCombine(route):
    target_file = os.path.join(os.path.dirname(route),
                               os.path.basename(route)+".ts")
    filelist = os.path.join(route, "filelist.txt")
    subprocess.run("ffmpeg -f concat -safe 0 -i {filelist} -c copy {target}"
                     .format(filelist=filelist, target=target_file))

def htmlGetCharset(bin_content:bytes):
    try:
        html_text = bin_content.decode("utf-8", "ignore")
        return re.search("charset=([^ ;'\">])*[ ;'\"]",html_text).group()[8:-1:]
    except:
        return None

def htmlAutoDecode(bin_content:bytes):
    codec = ["utf-8","gbk","gb2312"]
    c = htmlGetCharset(bin_content)
    if c != None:
        return bin_content.decode(c,"ignore")
    for c in codec:
        try:
            return bin_content.decode(c)
        except:
            pass
    return None

def htmlStrip(html_text:str):
    return html_text.replace("\n","").replace("\r","")