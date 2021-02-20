import m3u8,glob,os,subprocess

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