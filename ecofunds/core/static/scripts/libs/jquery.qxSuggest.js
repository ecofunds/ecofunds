

$.fn.suggest = function (settings) {
    /// <summary>Função autocomplete (dependência: qxDialog)</summary>
    /// <param name="settings" type="Object">{url, data, minChars, delay, isWebService, panelClass, searchClass, foundClass, loadingClass, onStart: function(event, data), onSelected: function(li, data), onLoadComplete(data), onRenderComplete(html)}</param>
    /// <returns type="jQuery" />

    var me = this;
    var xhr = null;
    var timeout = null;
    var text = "";
    var lastSearch = "";
    var lastResult = null;
    var panel = null;

    var removePanel = function () {
        $("#suggestList").remove();
    };
    var createPanel = function () {
        $(me.parent()).append("<div id=\"suggestList\" />");
        panel = $("#suggestList").addClass(settings.panelClass);
    };
    var loadComplete = function (html, status, xhr, isRendered) {
        me.removeClass(settings.loadingClass);

        if ($.isFunction(settings.onLoadComplete)) settings.onLoadComplete(html);

        removePanel();

        var obj = null;
        try { obj = $.parseJSON(html); }
        catch (ex) { obj = null; }

        var errorMessage = "";
        var position = me.position();
        var offset = me.offset();

        if (obj == null) {
            if ($.trim(html) != "") {
                createPanel();
                panel.html(html);
            }

        } else {
            if (obj.error) errorMessage = obj.errorMessage;
            else {
                if (obj.hasOwnProperty("d")) obj = obj.d;
                if (obj.suggestions.length > 0) {

                    createPanel();

                    panel.append("<ul />");
                    $.each(obj.suggestions, function (i, text) {
                        $("ul", panel).append("<li><a href=\"javascript:;\"><span class=\"" + settings.searchClass + "\">" + text + "</span></a></li>");
                    });
                }
            }
        }

        if (errorMessage == "") {
            if (panel != null) {
                var h = $(window).innerHeight() - (offset.top + me.outerHeight());
                if ($("ul", panel).height() < h) h = "auto";
                panel.css({ top: position.top + me.outerHeight(), left: position.left, width: me.innerWidth()/*, height: h*/ });

                $("li", panel).each(function (i) {
                    $("a", this).unbind("click");
                    $("a", this).click(function () {
                        me.val($(".search", this).text());
                        if ($.isFunction(settings.onSelected)) settings.onSelected($(this).parents("li"), obj != null ? obj.data[i] : null);

                        removePanel();
                    });
                });

                $("." + settings.searchClass, panel).each(function () {
                    var finded = $(this).text().replace(new RegExp("(" + text + ")(.*)", "gi"), "<span class=\"" + settings.foundClass + "\">\$1</span>\$2");
                    if ($(this).text().toLowerCase() == text.toLowerCase()) {
                        if ($.isFunction(settings.onSelected)) settings.onSelected($(this).parents("li"), obj != null ? obj.data[i] : null);
                    }
                    $(this).html(finded);
                });

                if ($.isFunction(settings.onRenderComplete)) settings.onRenderComplete(panel);

                document.onclick = function () { if (!isRendered) removePanel(); isRendered = false; };

                lastSearch = text;
            }
        }
        else {
            MessageBox.Show(errorMessage);
        }
        me.removeClass(settings.loadingClass);
        lastResult = html;
    };

    var start = function (event) {

        text = me.val();
        if (event.keyCode != 17) {

            if (xhr != null) xhr.abort();


            if (text.length >= settings.minChars) {

                me.addClass(settings.loadingClass);
                if (settings.data == undefined || settings.data == null) settings.data = {};
                if (settings.delay == undefined || settings.delay == null) settings.delay = 0;
                settings.data["search"] = text;

                if ($.isFunction(settings.onStart)) settings.onStart(event, settings.data);

                var postSuggest = function () {

                    if (timeout != null) clearTimeout(timeout);

                    var tokenInput = $("input[name='__RequestVerificationToken']:first");
                    if (tokenInput.length > 0)
                        settings.data.__RequestVerificationToken = tokenInput.val();
                    else {
                        tokenInput = $("input[name='csrfmiddlewaretoken']:first");
                        if (tokenInput.length > 0)
                            settings.data.csrfmiddlewaretoken = tokenInput.val();
                    }

                    var sendData = settings.data;
                    if (settings.isWebService) {
                        sendData = "{";
                        var i = 0;
                        for (var k in settings.data) {
                            if (i > 0) sendData += ", ";
                            sendData += k + ": \"" + settings.data[k] + "\"";
                            i++;
                        }
                        sendData += "}";
                    }
                    xhr = $.ajax({
                        url: settings.url,
                        type: "POST",
                        data: sendData,
                        dataType: "text",
                        success: loadComplete,
                        error: function (jqXHR, textStatus, errorThrown) {
                            me.removeClass(settings.loadingClass);
                        },
                        beforeSend: function (xhr) {
                            if (sendData.csrfmiddlewaretoken)
                                xhr.setRequestHeader('X-CSRFToken', sendData.csrfmiddlewaretoken);
                        }
                    });
                }

                if (text != lastSearch) {
                    if (settings.delay > 0) timeout = setTimeout(postSuggest, settings.delay);
                    else postSuggest();
                }
                else {
                    loadComplete(lastResult, "success", xhr, true);
                }


            } else {
                removePanel();
            }
        }
    };
    if (typeof (settings) == 'string' && settings == 'destroy') {
        me.unbind("keyup paste focusin");
    } else {
        settings = settings || {};
        if (settings.minChars == undefined || isNaN(settings.minChars)) settings.minChars = 1;
        if (settings.loadingClass == undefined) settings.loadingClass = "inputLoading";
        if (settings.panelClass == undefined) settings.panelClass = "suggestList";
        if (settings.searchClass == undefined) settings.searchClass = "search";
        if (settings.foundClass == undefined) settings.foundClass = "found";
        if (settings.isWebService == undefined) settings.isWebService = false;

        me.unbind("keyup paste focusin", start);
        me.bind("keyup paste focusin", start);
    }
    return me;
}