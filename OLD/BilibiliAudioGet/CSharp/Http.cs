using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net.Http;
using System.Net;

namespace BilibiliAudioGet
{
    class Http
    {
        public int DownloadSize { get; set; } = 0;

        public async Task<string> GetFromUrl(string url)
        {

            HttpClient client = new HttpClient(new HttpClientHandler() { AutomaticDecompression = DecompressionMethods.GZip });
            client.DefaultRequestHeaders.Add("User-Agent", "BilibiliAudioGet/2.33.33");
            try
            {
                string response = await client.GetStringAsync(url);
                return response;
            }
            catch
            {
               return "{\"code\":404}";
            }
        }

        public async Task<string> DownloadFormUrl(string url, string path)
        {
            HttpClient client = new HttpClient(new HttpClientHandler() { AutomaticDecompression = DecompressionMethods.GZip });
            client.DefaultRequestHeaders.Add("User-Agent", "BilibiliAudioGet/2.33.33");
            try
            {
                var response = await client.GetAsync(url);

                using (var stream = await response.Content.ReadAsStreamAsync())
                {
                    var fileInfo = new FileInfo(path);
                    using (var fileStream = fileInfo.OpenWrite())
                    {
                        await stream.CopyToAsync(fileStream);
                        return "";
                    }
                }
            }

            catch (Exception e)
            {
                return e.Message;
            }
        }
    }
}
