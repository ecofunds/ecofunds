define('gmaps', ['async!http://maps.googleapis.com/maps/api/js?v=3.12&key=AIzaSyBnFMm_tadKGcXD4tP93hKTI73HM2zsqFY&sensor=false'], function() {
    return google;
});


requirejs.config({
    baseUrl: '/static/js',
    waitSeconds: 300,
    paths: {
        jquery: 'jquery',
        jqueryui: 'jquery-ui.min',
        backbone : 'backbone-min',
        underscore: 'underscore-min',
        loogica: 'loogica_maps',
        marker: 'markerwithlabel_packed',
        infobox: 'infobox_packed',
        markerclusterer: 'markerclusterer_compiled',
        modelbinder: 'Backbone.ModelBinder-min',
        humanize: 'humanize.min'
    },
    shim: {
        jqueryui: {
            deps: ['jquery'],
            exports: 'ui'
        },
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
            deps: ['backbone', 'gmaps', 'marker', 'modelbinder', 'humanize'],
            exports: 'loogica'
        },
        markerclusterer: {
            deps: ['gmaps'],
            exports: 'markerclusterer'
        },
        modelbinder: {
            deps: ['backbone'],
            exports: 'modelbinder'
        },
        humanize: {
            exports: 'humanize'
        }
    }
});

require(["domReady!", "backbone", "loogica"], function(doc, Backbone, loogica, ui) {
    $('#id_map').css('height', global_map_height);
    $('#chart-view').hide();

    require(["marker", "markerclusterer"], function () {
        window.map_router = new loogica.MapRouterWithFilter();
        Backbone.history.start({pushState: false});
        window.map_router.navigate(default_domain, {trigger: true});
        $('.carregando.tela-mapa', '.mapa').hide();
    });
});
