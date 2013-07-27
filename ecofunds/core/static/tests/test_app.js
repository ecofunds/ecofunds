define('gmaps', ['async!http://maps.googleapis.com/maps/api/js?key=AIzaSyBnFMm_tadKGcXD4tP93hKTI73HM2zsqFY&sensor=false'], function() {
    return google;
});


requirejs.config({
    baseUrl: '/static/js',
    paths: {
        jquery: 'jquery',
        backbone : 'backbone-min',
        underscore: 'underscore-min',
        rio_data: 'neighborhood',
        loogica: 'loogica_maps',
        rio_data: 'neighborhood',
        marker: 'markerwithlabel_packed',
        infobox: 'infobox_packed',
        jasmine: 'tests/jasmine',
        'jasmine-html': 'tests/jasmine-html'
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
        },
        jasmine: {
            exports: 'jasmine'
        },
        'jasmine-html': {
            deps: ['jasmine'],
            exports: 'jasmine'
        }
    }
});

require(["domReady!", "backbone",
         "loogica", "jasmine-html"], function(doc, Backbone, loogica, jasmine) {

    var jasmineEnv = jasmine.getEnv();
    jasmineEnv.updateInterval = 1000;

    var htmlReporter = new jasmine.HtmlReporter();

    jasmineEnv.addReporter(htmlReporter);

    jasmineEnv.specFilter = function(spec) {
        return htmlReporter.specFilter(spec);
    };

    var currentWindowOnload = window.onload;

    var specs = [];
    specs.push('/static/js/tests/specs/RegionSpec.js');

    $(function(){
        require(specs, function(specs){
            jasmineEnv.execute();
        });
    });
});
