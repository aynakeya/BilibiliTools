var myScript = document.createElement('script');
myScript.textContent =`
var b_pipMode = null;
var barSelector = "#bilibiliPlayer > div.bilibili-player-context-menu-container.bilibili-player-context-menu-origin>ul";
var videoSelector = "#bilibiliPlayer > video";
var abc;
var switchpipmode = function(){
    if (b_pipMode){
        $("video").removeAttr("controls");
        $("div.bilibili-player-video-subtitle").css("z-index","");
        $("#pipswitch").text("开启画中画状态");
        b_pipMode = false;
    }
    else{
        $("video").attr("controls","controls");
        $("div.bilibili-player-video-subtitle").css("z-index","-1");
        b_pipMode = true;
        $("#pipswitch").text("关闭画中画状态");
    }
}
function addToToolBar(){
    if ($(barSelector).children().length == 6 && b_pipMode === null){
        var $il0 = $("<li></li>");
        $il0.addClass("context-line context-menu-function");
        var $a0 = $("<a></a>");
        $a0.addClass("context-menu-a js-action");
        $a0.attr("href","javascript:void(0);");
        $a0.attr("id","pipswitch");
        b_pipMode = false;
        $a0.text("开启画中画状态");
        $il0.append($a0);
        $a0.click(switchpipmode);
        $(barSelector).append($il0);
        clearTimeout(abc);
    }
    else{
        abc = setTimeout(addToToolBar,100);
    }
}
$(document).ready(addToToolBar);
`;
if (window.parent.document.body != null){
    window.parent.document.body.appendChild(myScript);
};
