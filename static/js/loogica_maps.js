define('loogica', ["domReady!", "jquery", "underscore",
         "backbone", "gmaps", "marker",
         "infobox"], function(doc, $, _, Backbone, google,
                              marker, infobox) {

    Region = Backbone.Model.extend({
        defaults: {
            name: "Region Name",
            polygons: [],
            region_visible: true,
            marker_visible: false,
            marker: null
        },
        initialize: function() {
            _.bindAll(this, 'area_visible');
            _.bindAll(this, 'marker_visible');
        },
        area_visible: function(mode) {
            if (mode == undefined) {
                return this.get('region_visible');
            }

            this.set('region_visible', mode);
            return mode;
        },
        marker_visible: function(mode) {
            if (mode == undefined) {
                return this.get('marker_visible');
            }

            this.set('marker_visible', mode);
            return mode;
        }
    });

    RegioView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            _.bindAll(this, 'render_polygon');
            _.bindAll(this, 'fill_region');
            _.bindAll(this, 'show_name');
            _.bindAll(this, 'toggle');
            this.model.bind('change:region_visible', this.toggle);
            this.model.bind('change:marker_visible', this.show_name);
            this.model.bind('fill_region', this.fill_region);
        },
        render: function() {
            var bounds = new google.maps.LatLngBounds();
            var polygons = this.model.get('polygons');

            this.model.gmaps_polygons = [];

            var self = this;
            _.each(polygons, function(polygon) {
                var gmap_polygon = self.render_polygon(polygon, bounds);
                self.model.gmaps_polygons.push(gmap_polygon);
            });

            this.model.bounds = bounds;
            if (this.model.get('marker_visible')) {
                this.show_name(this.model, true);
            }
        },
        show_name: function(model, show) {
            if (this.model.get('marker') == null) {
                var point_fix = this.model.get('name').length * 3;
                var marker = new MarkerWithLabel({
                    map: window.map_router.map,
                    raiseOnDrag: false,
                    draggable: false,
                    position: this.model.bounds.getCenter(),
                    labelContent: this.model.get('name'),
                    labelAnchor: new google.maps.Point(point_fix, 0),
                    labelClass: "labels",
                    labelStyle: {opacity: 0.75},
                    icon: 'images.png'
                });
                this.model.set({'marker': marker}, {silent: true});
            }
            this.model.get('marker').setVisible(show);
        },
        fill_region: function(color) {
            _.each(this.model.gmaps_polygons, function(polygon) {
                polygon.setOptions({ fillColor: color });
            });
        },
        toggle: function(model, visible) {
            _.each(this.model.gmaps_polygons, function(polygon) {
                polygon.setVisible(visible);
            });

            var marker = this.model.get('marker');
            if (marker && this.model.get('marker_visible')) {
                this.model.get('marker').setVisible(visible);
            }
        },
        render_polygon: function(polygon, bounds) {
            var coordinates = [];

            _.each(polygon.coordinates, function(coordinate) {
                var lat = coordinate[0];
                var lng = coordinate[1];
                var gmap_coordinate = new google.maps.LatLng(lat, lng);
                coordinates.push(gmap_coordinate);
                bounds.extend(gmap_coordinate);
            });


            var polygonOptions = {
                path: coordinates,
                strokeColor: "#FFFFFF",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "#0000FF",
                fillOpacity: 0.6,
                clickable: true
            };

            var gmapspolygon = new google.maps.Polygon(polygonOptions);

            var self_model = this.model;
            google.maps.event.addListener(gmapspolygon, "mouseover",
                function () {
                    self_model.trigger("fill_region", '#000');
            });

            google.maps.event.addListener(gmapspolygon, "mouseout",
                function () {
                    self_model.trigger("fill_region", '#0000FF');
            });

            gmapspolygon.setMap(window.map_router.map);
            return gmapspolygon;
        }
    });

    Place = Backbone.Model.extend({
    });
    Places = Backbone.Collection.extend({
        model: Place,
        parse: function(data, options) {
            return data.items;
        }
    });
    PlacesView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.collection.bind('reset', this.render);
        },
        render: function() {
            _.each(this.collection.models, function(place) {
                new PlaceView({model: place}).render();
            });
        }
    });
    PlaceView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render: function() {
            var lat = this.model.get('lat');
            var lng = this.model.get('lng');
            var myLatlng = new google.maps.LatLng(lat, lng);

            //XXX refatorar para algo melhor
            var _map = window.map_router.map;
            var scale = this.model.get('scale');
            var total = this.model.get('total_investment');
            var total_str = this.model.get('total_investment_str');

            var circle_options = {
                strokeColor: '#FF0000',
                strokeOpacity: 0.8,
                strokeWeight: 0,
                fillOpacity: 0.8,
                fillColor: '#8eb737',
                map: _map,
                center: myLatlng,
                radius: (total /100)
            };
            var circle = new google.maps.Circle(circle_options);
            var self_model = this.model;
            var info_window = new google.maps.InfoWindow({
                content: total_str
            });
            var marker = new MarkerWithLabel({
                position: myLatlng,
                draggable: false,
                map: _map,
                labelContent: total_str,
                labelAnchor: new google.maps.Point(22, 0),
                labelClass: "labels", // the CSS class for the label
                labelStyle: {opacity: 0.75},
                icon: 'a.png'
            });
            circle.bindTo('center', marker, 'position');
            google.maps.event.addListener(marker, "click",
                function() {
                    info_window.open(_map, marker);
            });
        }
    });

    Map = Backbone.Model.extend({});
    MapView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render: function() {
            var map = new google.maps.Map(document.getElementById('id_map'),
                                          this.model.toJSON());
            return map;
        }
    });

    MapRouter = Backbone.Router.extend({
        routes: {
            'investment' : 'fetch_investments',
            'project' : 'fetch_projects',
            'organization' : 'fetch_organizations'
        },
        initialize: function() {
            var _map = {
                zoom: 4,
                center: new google.maps.LatLng(-22.9488441857552033,
                                               -43.358066177368164),
                mapTypeId: google.maps.MapTypeId.SATELLITE,
                noClear: true,
                zoomControl: true,
                zoomControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_TOP
                },
                scaleControl: true,
                scaleControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_TOP
                },
                panControl: false,
                streetViewControl: false,
                scrollwheel: false
            };
            var map = new Map(_map);
            map_view = new MapView({model:map});
            this.map = map_view.render();
        },
        fetch_investments: function() {
            this.investment_places = new Places();
            this.investment_places.url = '/geo_api/investment/' + default_map_type;
            this.investment_places_view = new PlacesView({
                collection: this.investment_places
            });
            this.investment_places.fetch();
        },
        fetch_projects: function() {
            this.investment_places = new Places();
            this.investment_places.url = '/geo_api/project/' + default_map_type;
            this.investment_places_view = new PlacesView({
                collection: this.investment_places
            });
            this.investment_places.fetch();
        },
        fetch_organizations: function() {
            this.investment_places = new Places();
            this.investment_places.url = '/geo_api/organization/' + default_map_type;
            this.investment_places_view = new PlacesView({
                collection: this.investment_places
            });
            this.investment_places.fetch();
        }
    });

    return {
        Region: Region,
        RegioView: RegioView,
        Place: Place,
        PlaceView: PlaceView,
        Map: Map,
        MapView: MapView,
        MapRouter: MapRouter
    };
});
