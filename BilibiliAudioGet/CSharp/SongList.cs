using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BilibiliAudioGet
{
    class SongList
    {
        public Dictionary<string, string> SongDict { get; set; } = new Dictionary<string, string>();

        public void Add(string id, string name)
        {
            SongDict.Add(id, name);
        }

        public void Del(int index)
        {
            SongDict.Remove(SongDict.ElementAt(index).Key);
        }

        public void DelAll()
        {
            SongDict = new Dictionary<string, string>();
        }
    }
}
