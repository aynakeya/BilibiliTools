// ==UserScript==
// @name         BiliBili-EnablePIP
// @namespace    None
// @version      2.0.0
// @description  Enable Picture in Picture mode in Bilibli 在b站中打开画中画模式，使chrome能在b站使用画中画。
// @author       LXG_Shadow
// @match        https://www.bilibili.com/video/*
// @match        https://www.bilibili.com/bangumi/play/*
// @match        https://live.bilibili.com/*
// @run-at       document-end
// @grant        none
// ==/UserScript==

var REFRESH_TIME = 500;
var STRING_OPEN_PICTURE_IN_PICTURE = "显示画中画面板";
var STRING_CLOSE_PICTURE_IN_PICTURE = "隐藏画中画面板";
var BILIBILI_LIVE_REG = RegExp(/^http(s)?:\/\/([a-zA-Z0-9\.]+)?live\.bilibili/);
var IS_BILIBILI_LIVE = (window.location.href.match(BILIBILI_LIVE_REG) != null);
var STRING_BAR_SELECTOR = IS_BILIBILI_LIVE ?
    "div.bilibili-live-player > div.bilibili-live-player-context-menu-container>ul" :
    "#bilibiliPlayer > div.bilibili-player-context-menu-container.bilibili-player-context-menu-origin>ul";
var STRING_PIC_IN_PIC_SWITCH = "pictureInPictureSwitch";

var b_pipMode = false;
var switchPictureInPictureMode;


if (IS_BILIBILI_LIVE) {
    switchPictureInPictureMode = function () {
        if (b_pipMode) {
            $("video").removeAttr("controls");
            $("div.bilibili-live-player-video-controller").css("z-index", "");
            $("div.bilibili-live-player-video").css("z-index", "");
        } else {
            $("video").attr("controls", "controls");
            $("div.bilibili-live-player-video-controller").css("z-index", "-1");
            $("div.bilibili-live-player-video").css("z-index", "10");
        }
        b_pipMode = !b_pipMode;
        $("#" + STRING_PIC_IN_PIC_SWITCH).text(b_pipMode ? STRING_CLOSE_PICTURE_IN_PICTURE : STRING_OPEN_PICTURE_IN_PICTURE);
    }
} else {
    switchPictureInPictureMode = function () {
        if (b_pipMode) {
            $("video").removeAttr("controls");
            $("div.bilibili-player-video-subtitle").css("z-index", "");
        } else {
            $("video").attr("controls", "controls");
            $("div.bilibili-player-video-subtitle").css("z-index", "-1");
        }
        b_pipMode = !b_pipMode;
        $("#" + STRING_PIC_IN_PIC_SWITCH).text(b_pipMode ? STRING_CLOSE_PICTURE_IN_PICTURE : STRING_OPEN_PICTURE_IN_PICTURE);
    }
}

function addToToolBar() {
    if ($(STRING_BAR_SELECTOR) != null && document.getElementById(STRING_PIC_IN_PIC_SWITCH) === null) {
        var $il0 = $("<li></li>");
        $il0.addClass("context-line context-menu-function");
        $il0.attr("data-append", "1");
        var $a0 = $("<a></a>");
        $a0.addClass("context-menu-a js-action");
        $a0.attr("title", null);
        $a0.attr("href", "javascript:void(0);");
        $a0.attr("id", STRING_PIC_IN_PIC_SWITCH);
        $a0.attr("data-disabled", "0");
        $a0.text(b_pipMode ? STRING_CLOSE_PICTURE_IN_PICTURE : STRING_OPEN_PICTURE_IN_PICTURE);
        $a0.click(switchPictureInPictureMode);
        $il0.append($a0);
        $(STRING_BAR_SELECTOR).append($il0);
    }
}

(function () {
    'use strict';
    if (!window.jQuery) {
        var oScript = document.createElement('script');
        oScript.type = "text/javascript";
        oScript.src = "//s1.hdslb.com/bfs/static/jinkela/long/js/jquery/jquery1.7.2.min.js";
        document.head.appendChild(oScript);
    }
    window.onload = window.setInterval(addToToolBar, REFRESH_TIME);
})();