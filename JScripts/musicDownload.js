javascript: (function() {
	var qn = prompt("音频下载,选择清晰度:0,1,2", 2);
	// audio
	var au = /au[0-9]+/.exec(window.location.pathname)[0].substring(2);
	$.ajaxSetup({
		crossDomain: true,
		xhrFields: {
			withCredentials: true
		}
	});
	$.get("https://www.bilibili.com/audio/music-service-c/web/url?mid=8047632&privilege=2&quality="+qn+"&sid="+au,
	function(data, status) {
		var dlink = document.createElementNS("http://www.w3.org/1999/xhtml", "a");
		console.log(data);
		dlink.href = data["data"]["cdns"][0];
		console.log(dlink.href);
		var ev = document.createEvent("MouseEvents");
		ev.initMouseEvent("click", true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
		dlink.dispatchEvent(ev);
		alert("下载已开始");
	})
})();