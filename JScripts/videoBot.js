//not finish

function videoPlayer(id) {
    this.iframePlayer = "https://www.bilibili.com/blackboard/newplayer.html";
    this.id = id;
    this.createIframe= function(){
        var iframe = document.createElement('iframe');
        iframe.id = this.id;
        iframe.style = "width:100%;";
        document.body.appendChild(iframe);
    };

    this.playUrl = function (url) {

    };

    this.playVideo = function (bvid,cid) {

    };
}

(function() {
    var iframePlayer = "https://www.bilibili.com/blackboard/newplayer.html";
    var url = "https://www.bilibili.com/video/BV12K4y1s7DF?page=1";
    var bv = /BV[0-9]+/.exec(url)[0];
    var page = /page=[0-9]+/.exec($("#link2").val())[0].substring(5);
    var pages;
    $.get("https://api.bilibili.com/x/player/pagelist?bvid="+bv,function(data, status){
        
    });
	$("body").empty();
	// normal video
	if (typeof(window.__INITIAL_STATE__.bvid) != "undefined"){
		bv = window.__INITIAL_STATE__.bvid;
		cid = /cid=[0-9]+/.exec($("#link2").val())[0].substring(4);
	}
	// bangumi
	else{
		bv = window.__INITIAL_STATE__.epInfo.bvid;
		cid = window.__INITIAL_STATE__.epInfo.cid;
	}
})();