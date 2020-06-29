javascript: (function() {
    if (typeof(window.__INITIAL_STATE__.bvid) != "undefined"){
        var id = "";
        if (location.href.indexOf("av") !== -1){
            id = window.__INITIAL_STATE__.bvid;
        }else{
            id = "av"+window.__INITIAL_STATE__.aid;
        }
        try {
            location.href = "/"+id;
        }catch (e) {
            alert(id);
        }
	}else {
        alert("av"+window.__INITIAL_STATE__.epInfo.aid+"---"+window.__INITIAL_STATE__.epInfo.bvid);
    }
})();