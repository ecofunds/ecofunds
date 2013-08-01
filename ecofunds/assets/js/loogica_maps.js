define('loogica', ["domReady!", "jquery", "underscore",
         "backbone", "gmaps", "marker",
         "infobox"], function(doc, $, _, Backbone, google,
                              marker, infobox) {

    var no_url = $("#no_url").html();

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
            return data.map.items;
        }
    });
    PlacesView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.collection.bind('reset', this.render);
        },
        render: function() {
            _.each(this.collection.models, function(place) {
                var places_view = new PlaceView({model: place});
                if (default_map_type == "density/")
                    places_view.render_density();
                if (default_domain == "organization") {
                    places_view.render_cluster();
                    return;
                }
                if (default_map_type == "marker/")
                    places_view.render_marker();
            });
        }
    });
    PlaceView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render_marker: function() {
            var map_elements = [];
            var _map = window.map_router.map;

            var name = this.model.get('acronym');
            var lat = this.model.get('lat');
            var lng = this.model.get('lng');
            var url = this.model.get('url');
            var myLatlng = new google.maps.LatLng(lat, lng);

            var info_label = $("#title_" + default_domain).html();
            var info_text_source = $('#info_' + default_domain).html();
            var template = Handlebars.compile(info_text_source);

            var info_window = new google.maps.InfoWindow({
                content: template({label: info_label,
                                   no_url: no_url,
                                   name: name,
                                   url: url})
            });

            var marker = new google.maps.Marker({
                position: myLatlng,
                map: _map
            });
            map_elements.push(marker);

            google.maps.event.addListener(marker, "click",
                function() {
                    info_window.open(_map, marker);
            });

            this.model.set('map_elements', map_elements);
        },
        render_density: function() {
            var _map = window.map_router.map;

            var lat = this.model.get('lat');
            var lng = this.model.get('lng');
            var myLatlng = new google.maps.LatLng(lat, lng);
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
                radius: (scale * 10000)
            };
            var circle = new google.maps.Circle(circle_options);

            var map_elements = [];
            map_elements.push(circle);

            var info_label = $("#title_" + default_domain).html();
            var info_text_source = $('#info_' + default_domain + '_density').html();
            var template = Handlebars.compile(info_text_source);

            var info_window = new google.maps.InfoWindow({
                content: template({label: info_label,
                                   projects: this.model.get('projects'),
                                   value: total_str})
            });

            var marker = new MarkerWithLabel({
                position: myLatlng,
                draggable: false,
                map: _map,
                labelContent: total_str,
                labelAnchor: new google.maps.Point(50, 10),
                labelClass: "labels", // the CSS class for the label
                labelStyle: {opacity: 0.75},
                icon: 'a.png'
            });
            map_elements.push(marker);
            circle.bindTo('center', marker, 'position');
            google.maps.event.addListener(marker, "click",
                function() {
                    info_window.open(_map, marker);
            });

            this.model.set('map_elements', map_elements);
        },
        render_cluster: function() {
            var map_elements = [];
            var _map = window.map_router.map;

            var name = this.model.get('name');
            var lat = this.model.get('lat');
            var lng = this.model.get('lng');
            var url = "http://dummy";
            var myLatlng = new google.maps.LatLng(lat, lng);

            var marker = new google.maps.Marker({
                position: myLatlng,
                map: _map
            });
            map_elements.push(marker);

            this.model.set('map_elements', map_elements);
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
            'organization' : 'fetch_organizations',
            'clean_markers': 'clean_markers'
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
            default_map_type = 'density/';
            default_domain = 'investment';
            $("a[href=#investment]").parent().removeClass('inativa').addClass('ativa');
            $("a[href=#project]").parent().removeClass('ativa').addClass('inativa');
            $("a[href=#organization]").parent().removeClass('ativa').addClass('inativa');
            $(".opcoes .tipo").show();
            $("#filtro-investimentos").show();
            $("#filtro-projetos").hide();
            $("#filtro-organizacoes").hide();
            this.clean_markers();
            this.places = new Places();
            this.places.url = '/geo_api/investment/' + default_map_type;
            this.places_view = new PlacesView({
                collection: this.places
            });
            this.places.fetch();
        },
        fetch_projects: function() {
            default_map_type = 'marker/';
            default_domain = 'project';
            $("a[href=#investment]").parent().removeClass('ativa').addClass('inativa');
            $("a[href=#project]").parent().removeClass('inativa').addClass('ativa');
            $("a[href=#organization]").parent().removeClass('ativa').addClass('inativa');
            $(".opcoes .tipo").hide();
            $("#filtro-investimentos").hide();
            $("#filtro-projetos").show();
            $("#filtro-organizacoes").hide();
            this.clean_markers();
            this.places = new Places();
            this.places.url = '/api/geo/project/' + default_map_type;
            this.places_view = new PlacesView({
                collection: this.places
            });

            /* Protótipo do do filtro só pra fazer funcionar*/
            var filter_params = {}

            var el = $('form.projetos').find('[name="s_project_name"]');
            if (el.val() != 'Enter the name of a project' && el.val().length > 0) {
                filter_params.s_project_name = el.val()
            }

            var el = $('form.projetos').find('[name="s_country"]');
            if (el.val() != 'Enter the name of a country' && el.val().length > 0) {
                filter_params.s_country = el.val()
            }

            var el = $('form.projetos').find('[name="s_state"]');
            if (el.val() != 'Enter the name of a state' && el.val().length > 0) {
                filter_params.s_state = el.val()
            }

            var el = $('form.projetos').find('[name="s_organization"]');
            if (el.val() != 'Enter the name of an organization' && el.val().length > 0) {
                filter_params.s_organization = el.val()
            }

            this.places.fetch({data: $.param(filter_params)});
        },
        fetch_organizations: function() {
            default_map_type = 'marker/';
            default_domain = 'organization';
            $("a[href=#investment]").parent().removeClass('ativa').addClass('inativa');
            $("a[href=#project]").parent().removeClass('ativa').addClass('inativa');
            $("a[href=#organization]").parent().removeClass('inativa').addClass('ativa');
            $(".opcoes .tipo").hide();
            $("#filtro-investimentos").hide();
            $("#filtro-projetos").hide();
            $("#filtro-organizacoes").show();
            this.clean_markers();
            this.places = new Places();
            this.places.url = '/api/geo/organization/' + default_map_type;
            this.places_view = new PlacesView({
                collection: this.places
            });
            this.places.fetch({async: false});

            var markers = [];
            if (this.places) {
                _.each(this.places.models, function(marker) {
                    _.each(marker.get('map_elements'), function(element) {
                        markers.push(element);
                    });
                });
            }
            var cluster = new MarkerClusterer(window.map_router.map, markers);
            cluster.setGridSize(30);
            cluster.setMaxZoom(14);
            this.cluster = cluster;

        },
        clean_markers: function() {
            if (this.places) {
                _.each(this.places.models, function(marker) {
                    _.each(marker.get('map_elements'), function(element) {
                        element.setMap(null);
                    });
                });
            }
            if (this.cluster) {
                this.cluster.clearMarkers();
            }
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
