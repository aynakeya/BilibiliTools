javascript: (function() {
	//location.href = window.__INITIAL_STATE__.videoData.pic;
	var picurl;
	// video
	if (typeof(window.__INITIAL_STATE__.videoData) != "undefined"){
		picurl = window.__INITIAL_STATE__.videoData.pic;
	}else{
		// bangumi
		picurl =window.__INITIAL_STATE__.mediaInfo.cover;
	}
	window.open(picurl);
})();
