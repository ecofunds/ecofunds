(function ($) {
	// Return new instance of a class using an array of parameters.
	function instance(constructor, args) {

		function F() {
			return constructor.apply(this, args);
		}
		F.prototype = constructor.prototype;
		return new F();
	}

	// Return a property value by name (descendant of google.maps by default).
	function property(path, context) {

		path = path.split('.');

		if (context == '') context = window;
		else context = context || window.google.maps;

		if (path[0] in context) {
			if (path.length > 1) {
				return property(path.slice(1).join('.'), context[path[0]]);
			}
			else {
				return context[path[0]];
			}
		}
		else {
			throw new Error(path[0] + ' not found!');
		}
	}

	// Link an InfoWindow to a Map or Marker.
	// Adds 3 new functions to the Map or Marker:
	//   openInfoWindow, closeInfoWindow, and getInfoWindow
	// If a Marker, adds a getMarker function to the InfoWindow.
	function linkInfo(obj, info) {
		obj.openInfoWindow = function () {
			if (obj instanceof google.maps.Marker) {
				info.open(obj.getMap(), obj);
			}
			else {
				info.open(obj);
			}
		};
		obj.closeInfoWindow = function () {
			info.close();
		};
		obj.getInfoWindow = function () {
			return info;
		};
		if (obj instanceof google.maps.Marker) {
			info.getMarker = function () {
				return obj;
			};
		}
	}

	// Add events to an object.
	function addEvents(obj, events) {
		for (e in events) {
			(function (eventName, handlerName, once) {
				var handler = function () {
					property(handlerName, window).apply(this, arguments);
				};
				if (once) {
					google.maps.event.addListenerOnce(obj, eventName, handler);
				}
				else {
					google.maps.event.addListener(obj, eventName, handler);
				}
			}).apply(this, events[e]);
		}
	}

	// Traverses any plain object or array. When an object with valid keys
	// is encountered, it's converted to the indicated type.
	// This allows us to create instances of classes and reference built-in
	// constants within a simple JSON style object.
	//
	// Valid keys:
	//   cls    The name of a class constructor (descendant of google.maps).
	//     arg  Array of positional parameters for class constructor.
	//     nfo  Associated Info Window for class constructor.
	//     evt  Associated Maps Event Listeners for class constructor.
	//   div    Placeholder for DOM node.
	//   val    The name of a property or constant (descendant of google.maps).
	function parse(obj, div) {

		// Handle a div.
		if (obj === 'div') {
			return div;
		}

		if ($.isPlainObject(obj) || $.isArray(obj)) {
			// Handle a new class instance.
			if (obj.cls) {
				// Handle initialization parameters.
				if (obj.cls == 'MarkerClusterer') {
					obj.arg[0] = $(div).getMap();
					obj.arg[1] = $(div).getMarkers();
				}
				var args = [];

				if (obj.arg) {
					for (var a in obj.arg) {

						args.push(parse(obj.arg[a], div));
					}
				}

				var o = instance(property(obj.cls, obj.context), args);

				// Handle an associated InfoWindow.
				if (obj.nfo) {
					linkInfo(o, parse(obj.nfo, div));
				}
				// Handle events.
				if (obj.evt) {
					addEvents(o, obj.evt);
				}
				return o;
			}
			// Handle a property or constant.
			if (obj.val) {
				return property(obj.val);
			}
			// Handle any other iterable.
			for (var k in obj) {
				obj[k] = parse(obj[k], div);
			}
		}
		return obj;
	}

	// Converts collections of LatLng coordinates to a LatLngBounds.
	// Traverses markers and polyline/polygon paths.
	function toBounds(obj) {
		var bounds = new google.maps.LatLngBounds();
		if (obj instanceof google.maps.MVCArray ||
                $.isArray(obj) || $.isPlainObject(obj)) {
			for (var k in obj) {
				bounds.union(toBounds(obj[k]));
			}
		}
		else if (obj instanceof google.maps.LatLng) {
			bounds.extend(obj);
		}
		else if (obj instanceof google.maps.Marker) {
			bounds.extend(obj.getPosition());
		}
		else if (obj instanceof google.maps.Polyline) {
			bounds.union(toBounds(obj.getPath()));
		}
		else if (obj instanceof google.maps.Polygon) {
			bounds.union(toBounds(obj.getPaths()));
		}
		return bounds;
	}

	// Clear all objects and remove them.
	function removeObjects(name) {
		return function () {
			var div = $(this);
			// Get any existing objects.
			var objects = div.data(name);
			for (var o in objects) {
				// Clear it from the map.
				objects[o].setMap(null);
			}
			// Remove from div data.
			div.removeData(name);
		};
	}

	// Add and render an array of objects.
	function addObjects(name, obj) {
		return function () {
			if (obj) {
				var div = $(this);
				// Get a map reference.
				var map = div.data('map');
				// Get any existing objects.
				var objects = div.data(name) || [];
				for (var o in obj) {
					// Parse the marker.
					var object = parse(obj[o], this);
					// Render it to the map.
					object.setMap(map);
					// Add the marker to our array.
					objects.push(object);
				}
				// Save the marker array to div data.
				div.data(name, objects);
			}
		};
	}

	// Fit the map to the objects.
	function fitObjects(name, zoom) {
		return function () {
			var div = $(this);
			// Get a map reference.
			var map = div.data('map');
			// Get any existing objects.
			var objects = div.data(name);
			if (map && objects) {
				var bounds = toBounds(objects);
				if (zoom >= 0) {
					// Zoom specified: center map to the bounds.
					map.setZoom(zoom);
					map.setCenter(bounds.getCenter());
				}
				else {
					// No zoom: fit map to the bounds.
					map.fitBounds(bounds);
				}
			}
		};
	}

	var mapxhr = null;

	// Add our custom methods to jQuery.
	$.fn.extend({
		removeMarkers: function () {
			return this.each(removeObjects('markers'));
		},
		removePolylines: function () {
			return this.each(removeObjects('polylines'));
		},
		removePolygons: function () {
			return this.each(removeObjects('polygons'));
		},
		addMarkers: function (obj) {
			return this.each(addObjects('markers', obj));
		},
		addPolylines: function (obj) {
			return this.each(addObjects('polylines', obj));
		},
		addPolygons: function (obj) {
			return this.each(addObjects('polygons', obj));
		},
		fitMarkers: function (zoom) {
			return this.each(fitObjects('markers', zoom));
		},
		fitPolylines: function (zoom) {
			return this.each(fitObjects('polylines', zoom));
		},
		fitPolygons: function (zoom) {
			return this.each(fitObjects('polygons', zoom));
		},
		getMarkers: function () {
			// If 'this' is a collection, only returns objects from first.
			return this.data('markers');
		},
		getPolylines: function () {
			// If 'this' is a collection, only returns objects from first.
			return this.data('polylines');
		},
		getCircles: function () {
			// If 'this' is a collection, only returns objects from first.
			return this.data('circles');
		},
		getPolygons: function () {
			// If 'this' is a collection, only returns objects from first.
			return this.data('polygons');
		},
		getMap: function () {
			// If 'this' is a collection, only returns objects from first.
			return this.data('map');
		},
		applyMap: function (obj) {
			var objects = Array();
			objects['mkr'] = 'markers';
			objects['lbl'] = 'labels';
			objects['pln'] = 'polylines';
			objects['crl'] = 'circles';
			objects['pgn'] = 'polygons';
			objects['mkc'] = 'markersClusterer';

			return this.each(function () {
				var div = $(this);
				// Get rid of any existing objects.
				for (var k in objects) {
					removeObjects(objects[k]).call(this);
				}
				// Remove any existing map.
				div.removeData('map');
				// Parse the map.
				var map = parse(obj, div.children('div')[0]);
				// Save the map to div data.
				div.data('map', map);
				// Handle objects.
				for (var k in objects) {
					if (obj && k in obj) {

						addObjects(objects[k], obj[k]).call(this);
						// Auto-size map if no center or zoom given.
						if (!map.getCenter()) {
							fitObjects(objects[k], map.getZoom()).call(this);
						}
					}
				}
			});
		},
		initMap: function (sourceURL, data, callback) {
			return this.each(function () {
				var div = $(this);
				var mapdiv = div.children('div');

				if (!sourceURL)
					sourceURL = '/maps/source/' + div.attr('id').replace('id_', '');

				if (mapxhr != null) mapxhr.abort();

				mapxhr = $.ajax({
					async: true,
					data: data,
					dataType: 'json',
					url: sourceURL
				}).done(function (result) {
					if (result) {
						mapdiv.removeClass();
						div.applyMap(result);
						var mapimg = div.children('img');
						google.maps.event.addListenerOnce(div.data('map'),
                            'tilesloaded', function () {
                            	mapimg.css('z-index', -1);
                            }
                        );
					}
					if ($.isFunction(callback)) callback();
				});
				mapdiv.removeClass();
				div.applyMap(null);
			});
		}
	});
})(jQuery || django.jQuery);
