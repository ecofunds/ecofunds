define('gmaps', ['async!http://maps.googleapis.com/maps/api/js?key=AIzaSyBnFMm_tadKGcXD4tP93hKTI73HM2zsqFY&sensor=false'], function() {
    return google;
});


requirejs.config({
    baseUrl: '/static/js',
    waitSeconds: 300,
    paths: {
        jquery: 'jquery',
        backbone : 'backbone-min',
        underscore: 'underscore-min',
        loogica: 'loogica_maps',
        marker: 'markerwithlabel_packed',
        infobox: 'infobox_packed',
    },
    shim: {
        gmaps: {
            exports: 'google'
        },
        underscore: {
            exports: '_'
        },
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        marker: {
            deps: ['gmaps'],
            exports: 'marker'
        },
        infobox: {
            deps: ['gmaps'],
            exports: 'infobox'
        },
        loogica: {
            deps: ['backbone', 'gmaps', 'marker'],
            exports: 'loogica'
        }
    }
});

require(["domReady!", "backbone", "loogica"], function(doc, Backbone, loogica) {

    $(window).resize(function () {
        var h = $(window).height(),
            offsetTop = 40; // Calculate the top offset
        $('#map_canvas').css('height', (h - offsetTop));
    }).resize();

    require(["marker"], function () {
        $("#loader").hide();
        window.map_router = new loogica.MapRouter();
        Backbone.history.start({pushState: false});
        window.map_router.navigate('investments', {trigger: true});
    });
});
