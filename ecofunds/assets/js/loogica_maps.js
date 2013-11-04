define('loogica', ["domReady!", "jquery", "underscore",
         "backbone", "gmaps", "marker", "humanize",
         "infobox", "jqueryui"], function(doc, $, _, Backbone, google,
                              marker, infobox, ui) {

    var info_window = new google.maps.InfoWindow;

    var Filter = Backbone.Model.extend({
        toQueryOptions: function() {
            /* Filters empty model attributes to avoid misleading the backend filter.
            *  Ideally the backend should ignore invalid filter values/attributes.
            *  This can be implemented with Forms
            * */
            var options = {};
            _.each(this.attributes, function(v, k){
                if(this.get(k))
                    options[k] = v;
            }, this);
            return options;
        }
    });

    FilterView = Backbone.View.extend({
        initialize:function () {
            this._modelBinder = new Backbone.ModelBinder();
            this._modelBinder.bind(this.model, this.el);

            this.button = $('.ocultar-exibir-filtro', this.$el);
            this.button.bind('click', {el: this.$el}, this.togglePanel);
        },
        togglePanel: function(e) {
            el = e.data.el;
            el.toggleClass('aberto fechado');
        }
    });

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
                else //if (default_map_type == "marker/")
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
            var _map = window.map_router.map;

            var latlng = new google.maps.LatLng(this.model.get('lat'),
                                                this.model.get('lng'));

            var marker = new google.maps.Marker({
                position: latlng,
                map: _map
            });

            var source = $('#info_' + default_domain).html();
            var template = Handlebars.compile(source);
            var info_content = template(this.model.attributes);

            google.maps.event.addListener(marker, "click", function(){
                info_window.setContent(info_content);
                info_window.open(_map, marker);
            });

            var map_elements = [];
            map_elements.push(marker);

            this.model.set('map_elements', map_elements);
        },
        render_density: function() {
            var _map = window.map_router.map;

            var latlng = new google.maps.LatLng(this.model.get('lat'),
                                                  this.model.get('lng'));

            var circle = new google.maps.Circle({
                strokeColor: '#FF0000',
                strokeOpacity: 0.8,
                strokeWeight: 0,
                fillOpacity: 0.8,
                fillColor: '#8eb737',
                map: _map,
                center: latlng,
                radius: this.scaleAmountToRadius(this.model.get('total_investment'))
            });

            var marker = new MarkerWithLabel({
                position: latlng,
                draggable: false,
                map: _map,
                labelContent: Humanize.compactInteger(this.model.get('total_investment')),
                labelAnchor: new google.maps.Point(50, 10),
                labelClass: "labels", // the CSS class for the label
                labelStyle: {opacity: 0.75},
                icon: '/static/images/ico/ico-none.png'
            });

            circle.bindTo('center', marker, 'position');

            var source = $('#info_' + default_domain + '_density').html();
            var template = Handlebars.compile(source);
            var info_content = template(this.model.attributes);

            google.maps.event.addListener(marker, "click", function(){
                info_window.setContent(info_content);
                info_window.open(_map, marker);
            });

            var map_elements = [];
            map_elements.push(circle);
            map_elements.push(marker);

            this.model.set('map_elements', map_elements);
        },
        scaleAmountToRadius: function(value) {
            var radiusOffset = 150000;
            var radiusMax = 500000;
            var radiusRange = radiusMax - radiusOffset;
            var stepRange = 100;
            var stepValue = radiusRange / stepRange;
            var stepIgnore = 30;
            var stepMin = 0;

            var tens = Number(value).toString().length - 1;
            var ones = Number(Number(value).toString()[0]);

            var stepCount = (tens * 10) + ones;

            var radius = Math.max(stepCount - stepIgnore, stepMin) * stepValue + radiusOffset;

            // console.debug(stepValue, tens, ones, stepCount, value, radius);

            return radius;
        }
    });

    Map = Backbone.Model.extend({
        defaults: {
            zoom: 4,
            center: new google.maps.LatLng(-13.297538592394982,
                                           -54.24283180236819),
            mapTypeId: google.maps.MapTypeId.SATELLITE,
            noClear: true,
            zoomControl: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.RIGHT_TOP
            },
            scaleControl: true,
            scaleControlOptions: {
                position: google.maps.ControlPosition.RIGHT_BOTTOM
            },
            panControl: false,
            streetViewControl: false,
            scrollwheel: false
        }
    });
    MapView = Backbone.View.extend({
        initialize: function() {
            this.map = new google.maps.Map(document.getElementById('id_map'),
                                          this.model.toJSON());

            this.slider = $('.slider-control').slider({
                orientation: "vertical",
                range: "min",
                min: 2,     // Determina o valor mínimo
                max: 14,    // Determina o valor máximo
                step: 1,    // Determina a quantidade de passos
                value: 4   // Determina o valor inicial
            });

            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
            $('.zoom-in').click({model: this.model}, this.zoomIn);
            $('.zoom-out').click({model: this.model}, this.zoomOut);
            this.slider.on('slidestop', {model: this.model}, this.zoom);
        },
        render: function() {
            var zoom = this.model.get('zoom');
            this.map.setZoom(zoom);
            this.slider.slider('value', zoom);
            return this.map;
        },
        zoomIn: function(e){
            var model = e.data.model;
            model.set('zoom', model.get('zoom') + 1);
        },
        zoomOut: function(e) {
            var model = e.data.model;
            model.set('zoom', model.get('zoom') - 1);
        },
        zoom: function(e, ui) {
            var model = e.data.model;
            model.set('zoom', ui.value);
        },
        center: function(lat, lng) {
            var center = new google.maps.LatLng(lat, lng);
            this.map.setCenter(center);
        }
    });

    MapRouter = Backbone.Router.extend({
        routes: {
            'investment' : 'fetch_investments',
            'project' : 'fetch_projects',
            'organization' : 'fetch_organizations',
            'clean_markers': 'clean_markers',
            'filter/:domain/:id': 'fetch_single'
        },
        initialize: function() {
            this.map_view = map_view = new MapView({model: new Map});
            this.map = this.map_view.render();
        },
        fetchPlaces: function(domain, async) {
            // Default value true
            async = typeof async !== 'undefined' ? async : true;

            this.places.fetch({async: async});
        },
        toggleFilter: function(domain) {
            /* Encapsula ativação e desativação de filtros.
             * Com eventual refatoração do css, esse código pode ser simplificado
             * usando toggle do Jquery, eliminando o else.
             */
            var options = [
                {domain: 'investment', menu: 'a[href$=#investment]', panel: "#filtro-investimentos" },
                {domain: 'project', menu: 'a[href$=#project]', panel: "#filtro-projetos" },
                {domain: 'organization', menu: 'a[href$=#organization]', panel: "#filtro-organizacoes" }
            ]

            _.each(options, function(o){
                if(o.domain == domain){
                    $(o.menu).removeClass('inativo').addClass('ativo');
                    $(o.panel).show();
                }
                else {
                    $(o.menu).removeClass('ativo').addClass('inativo');
                    $(o.panel).hide();
                }
            }, this);
        },
        fetch_investments: function() {
            default_map_type = 'density/';
            default_domain = 'investment';
            this.toggleFilter(default_domain);
            $(".opcoes .tipo").show();
            this.clean_markers();
            this.places = new Places();
            this.places.url = '/api/geo/investment/' + default_map_type;
            this.places_view = new PlacesView({
                collection: this.places
            });
            this.fetchPlaces(default_domain, false);
        },
        fetch_projects: function() {
            default_map_type = 'marker/';
            default_domain = 'project';
            this.toggleFilter(default_domain);
            $(".opcoes .tipo").hide();
            this.clean_markers();
            this.places = new Places();
            this.places.url = '/api/geo/project/' + default_map_type;
            this.places_view = new PlacesView({
                collection: this.places
            });

            this.fetchPlaces(default_domain, false);
        },
        fetch_organizations: function() {
            default_map_type = 'marker/';
            default_domain = 'organization';
            this.toggleFilter(default_domain);
            $(".opcoes .tipo").hide();
            this.clean_markers();
            this.places = new Places();
            this.places.url = '/api/geo/organization/' + default_map_type;
            this.places_view = new PlacesView({
                collection: this.places
            });

            this.fetchPlaces(default_domain, false);

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
        fetch_single: function(domain, id) {
            this.toggleFilter(domain);
            $(".opcoes .tipo").hide();
            this.clean_markers();
            this.places = new Places();
            this.places.url = '/detail/api/' + domain + '/' + id;
            this.places_view = new PlacesView({
                collection: this.places
            });

            this.fetchPlaces(domain, false);
            var lat = this.places.models[0].get('lat');
            var lng = this.places.models[0].get('lng');
            this.map_view.center(lat, lng);
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

    MapRouterWithFilter = MapRouter.extend({
        initialize: function() {
            MapRouterWithFilter.__super__.initialize.apply(this, arguments);

            /* Initialize filters */
            this.projectFilterView = new FilterView({el: '#project-filter', model: new Filter});
            this.listenTo(this.projectFilterView.model, 'change', this.fetch_projects);

            this.organizationFilterView = new FilterView({el: '#organization-filter', model: new Filter});
            this.listenTo(this.organizationFilterView.model, 'change', this.fetch_organizations);

            this.investmentFilterView = new FilterView({el: '#investment-filter', model: new Filter});
            this.listenTo(this.investmentFilterView.model, 'change', this.fetch_investments);
        },
      fetchPlaces: function(domain, async) {
            // Default value true
            async = typeof async !== 'undefined' ? async : true;

            var views = {
                investment: this.investmentFilterView,
                project: this.projectFilterView,
                organization: this.organizationFilterView
            }

            var view = views[domain];

            this.places.fetch({
                data: $.param(view.model.toQueryOptions()),
                async: async
            });
        }
    });

    return {
        Region: Region,
        RegioView: RegioView,
        Place: Place,
        PlaceView: PlaceView,
        Map: Map,
        MapView: MapView,
        MapRouter: MapRouter,
        MapRouterWithFilter: MapRouterWithFilter
    };
});
