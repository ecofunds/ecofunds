/// <reference path="jquery-1.7.1-vsdoc.js" />

(function ($) {
    $.getCSRF = function (tokenWindow, appPath) {
        // HtmlHelper.AntiForgeryToken() must be invoked to print the token.
        tokenWindow = tokenWindow && typeof tokenWindow === typeof window ? tokenWindow : window;

        appPath = appPath && typeof appPath === "string" ? "_" + appPath.toString() : "";
        // The name attribute is either __RequestVerificationToken,
        // or __RequestVerificationToken_{appPath}.
        var tokenName = "csrfmiddlewaretoken" + appPath;

        // Finds the <input type="hidden" name={tokenName} value="..." /> from the specified window.
        // var inputElements = tokenWindow.$("input[type='hidden'][name=' + tokenName + "']");
        var inputElements = tokenWindow.document.getElementsByTagName("input");
        for (var i = 0; i < inputElements.length; i++) {
            var inputElement = inputElements[i];
            if (inputElement.type === "hidden" && inputElement.name === tokenName) {
                return {
                    name: tokenName,
                    value: inputElement.value
                };
            }
        }
    };

    $.appendCSRF = function (data, token) {
        // Converts data if not already a string.
        if (data && typeof data !== "string") {
            data = $.param(data);
        }

        // Gets token from current window by default.
        token = token ? token : $.getCSRF(); // $.getAntiForgeryToken(window).

        data = data ? data + "&" : "";
        // If token exists, appends {token.name}={token.value} to data.
        return token ? data + encodeURIComponent(token.name) + "=" + encodeURIComponent(token.value) : data;
    };

    // Wraps $.post(url, data, callback, type) for most common scenarios.
    $.postCSRF = function (url, data, callback, type) {
        return $.post(url, $.appendCSRF(data), callback, type);
    };

    // Wraps $.ajax(settings).
    $.ajaxCSRF = function (settings) {
        // Supports more options than $.ajax(): 
        // settings.token, settings.tokenWindow, settings.appPath.
        var token = settings.token ? settings.token : $.getCSRF(settings.tokenWindow, settings.appPath);
        var before = settings.beforeSend;

        settings.beforeSend = function (xhr) {
            if ($.isFunction(before)) before(xhr);
            xhr.setRequestHeader('X-CSRFToken', token.value);
        }

        settings.data = $.appendCSRF(settings.data, token);
        return $.ajax(settings);
    };
})(jQuery);