using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BilibiliAudioGet
{
    class API
    {
        public delegate void UpdateStatus();
        public event UpdateStatus Update;

        private readonly Http HttpClient = new Http();
        private readonly SongList SongList = new SongList();
        public string DownloadStatus { get; set; } = "";

        private async Task<int> Download(string id, string name, string appPath)
        {
            string api = "http://api.bilibili.com/audio/music-service-c/url?mid=1&mobi_app=iphone&platform=ios&privilege=2&quality=2&songid=";
            string url = api + id;

            string json = await HttpClient.GetFromUrl(url);
            
            JObject jsonReader = JObject.Parse(json);

            if (jsonReader["code"].ToString() == "0")
            {
                string durl = jsonReader["data"]["cdns"][0].ToString();

                string i = "";
                int j = 0;
                string path = appPath + "/Music/" + name + i + ".m4a";
                while (File.Exists(path))
                {
                    j++;
                    i = j.ToString();
                    path = appPath + "/Music/" + name + i + ".m4a";
                }

                await HttpClient.DownloadFormUrl(durl, path);
            }
            else
            {
                return 404;
            }
            return 200;
        }

        public async Task<bool> DownloadAll(string appPath)
        {
            try
            {
                int Status = 0;
                Dictionary<string, string> dict = SongList.SongDict;
                int i = 1;
                int all = dict.Count();

                if (!Directory.Exists(appPath + "/Music/"))
                {
                    Directory.CreateDirectory(appPath + "/Music/");
                }

                foreach (var item in dict)
                {
                    string index = " ( " + i.ToString() + " / " + all.ToString() + " )";
                    string id = item.Key;
                    string name = item.Value;
                    DownloadStatus = "Downloading: " + name + index;
                    Update();
                    Status = await Download(id, name, appPath);

                    if (Status == 200)
                    {
                        DownloadStatus = "Download Completed: " + name + index;
                    }
                    else if (Status == 404)
                    {
                        DownloadStatus = "Download Failed: " + name + " has been removed." + index;
                    }
                    else if (Status == 503)
                    {
                        DownloadStatus = "Download Failed: API Error" + index;
                    }
                    Update();
                    i = i + 1;
                }
                return true;
            }
            catch (Exception e)
            {
                DownloadStatus = e.Message;
                Update();
                return false;
            } 
        }

        public async Task<string> GetSingle(string id)
        {
            string api = "https://www.bilibili.com/audio/music-service-c/web/song/info?sid=";
            string url = api + id;
            string json = await HttpClient.GetFromUrl(url);
            string name = "";
            JObject jsonReader = JObject.Parse(json);
            if (jsonReader["code"].ToString() == "0")
            {

                name = jsonReader["data"]["title"].ToString();
                string artist = jsonReader["data"]["author"].ToString();
                if (!SongList.SongDict.ContainsKey(id))
                {
                    SongList.Add(id, name);
                    name = name + "      " + artist;
                    return name;
                }
            }
            else
            {
                DownloadStatus = "Single Not Found";
                Update();
            }
            return "";
        }

        public async Task<List<string>> GetPlayList(string id)
        {
            

            string info_api = "https://www.bilibili.com/audio/music-service-c/web/menu/info?sid=";
            string info_url = info_api + id;
            string info_json = await HttpClient.GetFromUrl(info_url);
            JObject jsonReader = JObject.Parse(info_json);
            if (jsonReader["code"].ToString() == "0")
            {
                string title = jsonReader["data"]["title"].ToString();
                DownloadStatus = "PlayList: " + title;
            }
            else if (jsonReader["code"].ToString() == "72000000")
            {
                DownloadStatus = "PlayList  Not Found";
            }
            Update();

            List<string> nameList = new List<string>();
            string detail_api = "https://www.bilibili.com/audio/music-service-c/web/song/of-menu?pn=1&ps=1000&sid=";
            string detail_url = detail_api + id;
            string detail_json = await HttpClient.GetFromUrl(detail_url);
            jsonReader = JObject.Parse (detail_json);

            if (jsonReader["code"].ToString() == "0")
            {
                int count = jsonReader["data"]["data"].Count();
                for (int i = 0; i < count; i++)
                {
                    string name = jsonReader["data"]["data"][i]["title"].ToString();
                    string sid = jsonReader["data"]["data"][i]["id"].ToString();
                    string artist = jsonReader["data"]["data"][i]["author"].ToString();

                    if (SongList.SongDict.ContainsKey(sid) == false)
                    {
                        nameList.Add(name + "       " + artist);
                        SongList.Add(sid, name);
                    }

                }

                
            }
            return nameList;
        }

        public void RemoveAll()
        {
            SongList.DelAll();
        }

        public void Remove(int index)
        {
            SongList.Del(index);
        }
    }
}
