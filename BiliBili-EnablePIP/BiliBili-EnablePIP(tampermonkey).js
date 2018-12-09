// ==UserScript==
// @name         BiliBili-EnablePIP
// @namespace    None
// @version      1.0.3
// @description  Enable Picture in Picture mode in Bilibli 在b站中打开画中画模式，使chrome/safair能在b站使用画中画。
// @author       LXG_Shadow
// @match        https://www.bilibili.com/video/*
// @match        https://www.bilibili.com/bangumi/play/*
// @run-at       document-end
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    var b_pipMode = null;
    var barSelector = "#bilibiliPlayer > div.bilibili-player-context-menu-container.bilibili-player-context-menu-origin>ul";
    var videoSelector = "#bilibiliPlayer > video";
    var abc;
    var switchpipmode = function() {
        if (b_pipMode) {
            $("video").removeAttr("controls");
            $("div.bilibili-player-video-subtitle").css("z-index", "");
            b_pipMode = false;
            $("#pipswitch").text("开启画中画状态");
        } else {
            $("video").attr("controls", "controls");
            $("div.bilibili-player-video-subtitle").css("z-index", "-1");
            b_pipMode = true;
            $("#pipswitch").text("关闭画中画状态");
        }
    }
    function addToToolBar() {
        if ($(barSelector).children().length == 6 && b_pipMode === null) {
            var $il0 = $("<li></li>");
            $il0.addClass("context-line context-menu-function");
            var $a0 = $("<a></a>");
            $a0.addClass("context-menu-a js-action");
            $a0.attr("href", "javascript:void(0);");
            $a0.attr("id", "pipswitch");
            b_pipMode = false;
            $a0.text("开启画中画状态");
            $a0.click(switchpipmode);
            $il0.append($a0);
            $(barSelector).append($il0);
            clearTimeout(abc);
        } else {
            abc = setTimeout(addToToolBar, 100);
        }
    }
    if (!window.jQuery){
        var oScript = document.createElement('script');
        oScript.type = "text/javascript";
        oScript.src="//s1.hdslb.com/bfs/static/jinkela/long/js/jquery/jquery1.7.2.min.js";
        document.head.appendChild(oScript);
    }
    window.onload=addToToolBar;
})();