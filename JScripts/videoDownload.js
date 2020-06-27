javascript: (function() {
	var qn = prompt("视频下载,选择清晰度:116,112,80,74,64,48,32,16", 116);
	var bv = window.__INITIAL_STATE__.bvid;
	var cid = /cid=[0-9]+/.exec($("#link2").val())[0].substring(4);
	$.ajaxSetup({
		crossDomain: true,
		xhrFields: {
			withCredentials: true
		}
	});
	$.get("https://api.bilibili.com/x/player/playurl?bvid=" + bv + "&cid=" + cid + "&qn=" + qn + "&type=&otype=json",
	function(data, status) {
		var dlink = document.createElementNS("http://www.w3.org/1999/xhtml", "a");
		dlink.href = data.data.durl[0]["url"].replace("http", "https");
		dlink.download = "a.flv";
		var ev = document.createEvent("MouseEvents");
		ev.initMouseEvent("click", true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
		dlink.dispatchEvent(ev);
		alert("待下载开始后,刷新页面来播放视频");
	})
})();