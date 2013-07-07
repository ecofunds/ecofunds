(function ($) {
    $(document).ready(function () { 
        //Expande os filtros
        //Ver mais/Ver menos nos filtros        
        showFilterMap();

        // Estiliza os scrolls dos filtros do mapa
        $('.form-filtros','.area-filtros-mapa').jScrollPane({
            showArrows: false,
            arrowScrollOnHover: true,
            verticalDragMinHeight: 20
        });

        //Cria os efeitos de hover do scroll
        $('.jspTrack', '.form-filtros').hide();
        $('.jspScrollable','.area-filtros-mapa').mouseenter(function(){
            $(this).find('.jspTrack').stop(true, true).fadeIn('slow');
        });
        $('.jspScrollable','.area-filtros-mapa').mouseleave(function(){
            $(this).find('.jspTrack').stop(true, true).fadeOut('slow');
        });         
    });
})(jQuery);


// Define the overlay, derived from google.maps.OverlayView
function Label(opt_options) {
    // Initialization
    this.setValues(opt_options);

    // Label specific
    var span = this.span_ = document.createElement('span');
    span.style.cssText = 'position: relative; left: -50%; top: -8px; ';

    var div = this.div_ = document.createElement('div');
    div.className = 'label';
    div.appendChild(span);
    div.style.cssText = 'position: absolute; display: none';
};
Label.prototype = new google.maps.OverlayView;

// Implement onAdd
Label.prototype.onAdd = function () {
    var pane = this.getPanes().overlayMouseTarget;
    pane.appendChild(this.div_);

    // Ensures the label is redrawn if the text or position is changed.
    var me = this;
    this.listeners_ = [
   google.maps.event.addListener(this, 'position_changed',
       function () { me.draw(); }),
   google.maps.event.addListener(this, 'text_changed',
       function () { me.draw(); })
 ];
};

// Implement onRemove
Label.prototype.onRemove = function () {
    this.div_.parentNode.removeChild(this.div_);

    // Label is removed from the map, stop updating its position/text.
    for (var i = 0, I = this.listeners_.length; i < I; ++i) {
        google.maps.event.removeListener(this.listeners_[i]);
    }
};

// Implement draw
Label.prototype.draw = function () {
    var projection = this.getProjection();
    var position = projection.fromLatLngToDivPixel(this.get('position'));
    var zIndex = this.get('zIndex');

    var div = this.div_;
    div.style.left = position.x + 'px';
    div.style.top = position.y + 'px';
    div.style.display = 'block';
    div.style.zIndex = zIndex + 1000;
    this.span_.innerHTML = this.get('text').toString();
};

Funbio.Ecofunds.Map = function () {
    var div = null;
    var map = null;
    var mapHeight = 0;
    var me = this;
    var slider = null;

    var currentFilter = null;
    var currentInfoWindow = null;
    var currentPolygonFillColor = null;
    var currentTab = null;
    var timeoutFilters = null;
    var timeoutFiltersDelay = 1000;

    var fullScreen = false;

	var me = this;
	var center = null;
	


    this.update = function()
    {
		var form = $(".form-filtros:visible");

        if (form.hasClass("projetos"))
        {
            data = getSendData($("form.projetos"));
            loadSource('project', data);
        }
        else if (form.hasClass("organizacoes"))
        {
            data = getSendData($("form.organizacoes"));
            loadSource('organization', data);
        }
        else if (form.hasClass("investimentos")) 
        {
            data = getSendData($("form.investimentos"));
            loadSource('investment', data);
        }
    }
    this.initMap = function()
    {
        div = $('div.gmap:visible');
        map = div.getMap();
        mapHeight = div.height();

        $(map.controls[google.maps.ControlPosition.TOP_RIGHT].b).wrap('<div class="container" />');

        google.maps.event.addListener(map, 'idle', me.mapLoaded);
        google.maps.event.addListener(map, 'zoom_changed', function () {
            var val = map.getZoom();
            slider.slider('value', val);
        });
        $('.carregando.tela-mapa', '.mapa').hide();


		/*
		if(navigator.geolocation)
		{
			navigator.geolocation.getCurrentPosition(function(position){
				console.log('Position', position);
				center = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

				if(map)
				{
					map.setZoom(5);	
					map.setCenter(center);
				}
			});
		}*/


		$.get("/ajax/project/geoip", function(loc, status){
		if(status == "success" && loc)
			{
				center = new google.maps.LatLng(loc.latitude, loc.longitude);

				if(map)
				{
					map.setZoom(4);	
					map.setCenter(center);
				}
			}

		}, "json");

    };
    this.init = function () {
        
		function bindSelectAll(checkName, textName, hint) {
		return function (contexto) {
			var cb = $(checkName, contexto);
			var control = $(textName, contexto);
			if (control.length == 0) {
				console.error('Argumentos inválidos:', checkName, textName);
				return;
			}

			console.log('Binding', cb.get(0), 'to', control.get(0));
			console.log('Control = ', control.val());
			console.log('Checkbox = ', cb.attr('checked'));

			if (control.val() && control.val() != control.attr('placeholder')) {
				cb.attr('checked', null);
				console.log('Checkbox not checked');
			}
			else {
				cb.attr('checked', 'checked');
				console.log('Checkbox checked');
			}
			cb.change();

			var tag = control.get(0).tagName;
			cb.change(function (evt) {
				console.log('Checkbox changed', this.checked);
				console.log(tag);
				if (this.checked) {
					control.val('');

					console.log('control', control);
					if (tag == 'INPUT') {
						control.keyup();
					}
					else if (tag == 'SELECT') {
						$('select', contexto).qxStylingForms();
						me.update();
					}
					else
						control.change();
				}
				else
					control.focus();


			});
			var textEvent = tag == 'INPUT' ? 'keyup' : 'change';
			control.bind(textEvent, function () {
				console.log('Control changed', this.value);
				var checked = (this.value.length == 0) ? 'checked' : null;
				cb.attr('checked', checked);
				cb.qxStylingForms();
			});

		};
	}

	$('form.projetos, form.organizacoes, form.investimentos').each(function(){


	var contexto = $(this);
	bindSelectAll('#id_s_all_project_name', '#id_s_project_name')(contexto);
	bindSelectAll('#id_s_all_organizations', '#id_s_organization')(contexto);
	bindSelectAll('#id_s_all_investments', '#id_s_investment')(contexto);
	bindSelectAll('#id_s_all_investments_focus', '#id_s_investments_focus')(contexto);

	bindSelectAll("#id_s_all_type_investments", "#id_s_investment_type")(contexto);

	bindSelectAll("#id_s_all_project_activity_type", "#id_s_project_activity_type")(contexto);
	bindSelectAll('#id_s_all_type_organizations', '#id_s_organization_type')(contexto);
	bindSelectAll('#id_s_all_investment_date', '#id_s_investment_date_from, #id_s_investment_date_to')(contexto);


	bindSelectAll('#id_s_all_investments_received', '#id_s_estimated_investments_value_from, #id_s_estimated_investments_value_to')(contexto);
	bindSelectAll('#id_s_all_investments_value', '#id_s_investment_from, #id_s_investment_to')(contexto);
	bindSelectAll('#id_s_all_investments_date', '#id_s_investment_date_from, #id_s_investment_date_to', 'date')(contexto);

	
	createProjectSuggest('.projetos #id_s_project_name');
	createProjectSuggest($('form.investimentos').get(0).s_project_name);

	
	createOrganizationSuggest('.projetos #id_s_organization');
	createOrganizationSuggest($('form.organizacoes').get(0).s_organization);
	createOrganizationSuggest($('form.investimentos').get(0).s_organization);

	
	createCountrySuggest('.projetos #id_s_country');
	createCountrySuggest($('form.organizacoes').get(0).s_country);
	createCountrySuggest($('form.investimentos').get(0).s_country);

	
	
	createRegionSuggest($('form.projetos').get(0).s_state);
	createRegionSuggest($('form.organizacoes').get(0).s_state);
	createRegionSuggest($('form.investimentos').get(0).s_state);



	});


        $(".qx-stylingForms-radio, input", ".opcoes .tipo").click(function () {
            me.update();
        });

        $("a.link", ".area-filtros-mapa .opcoes .visualizacao").unbind('click').click(function () {
            $("li.item", ".area-filtros-mapa .opcoes .visualizacao").removeClass("ativo").addClass("inativo");
            $("a.link", ".area-filtros-mapa .opcoes .visualizacao").removeClass("ativo").addClass("inativo");

            $(this).removeClass("inativo").addClass("ativo");
            $(this).parents("li").removeClass("inativo").addClass("ativo");

            me.update();
        });

        $("a.link", ".graficos .visualizacao").unbind('click').click(function(){
            $("li.item", ".graficos .visualizacao").removeClass("ativo").addClass("inativo");
            $("a.link", ".graficos .visualizacao").removeClass("ativo").addClass("inativo");

            $(this).removeClass("inativo").addClass("ativo");
            $(this).parents("li").removeClass("inativo").addClass("ativo");

            me.update();
        });

        $('.form-filtros').on('keyup paste', ':text', function (event) {

            currentFilter = $(this);

            if (timeoutFilters != null) clearTimeout(timeoutFilters);
            if (event.which == 13) {
                me.update();
                event.preventDefault();
            }
            else {
                timeoutFilters = setTimeout(function () { me.update(); }, timeoutFiltersDelay);
            }
        });

        $('.form-filtros').on('click', ':radio, :checkbox', function (event) {
            currentFilter = $(this);
            if (timeoutFilters != null) clearTimeout(timeoutFilters);
            timeoutFilters = setTimeout(function () { me.update(); }, timeoutFiltersDelay);
        });
        $('.form-filtros').on('change', 'select', function () {
            currentFilter = $(this);
            me.update();
        });

        $('#bt-terrain').unbind('click').click(function(){
            me.changeMapType(google.maps.MapTypeId.TERRAIN);
        });

        $('#bt-hybrid').unbind('click').click(function(){
            me.changeMapType(google.maps.MapTypeId.HYBRID);
        });

        $('#bt-fullscreen').click(me.toggleFullScreen);
            
        /* Função utilizada para criar o slider do mapa */
        var gmin = 2; //Determina o valor mínimo
        var gmax = 14; //Determina o valor máximo
        var gvalue = 4; //Determina o valor inicial
        var gstep = 1; //Determina a quantidade de passos

        slider = $('.slider-control').slider({
            orientation: "vertical",
            range: "min",
            min: gmin,
            max: gmax,
            step: gstep,
            value: gvalue,
            stop: function (event, ui) {
                var val = ui.value;
                me.changeZoom(val);
            }
        });

        /* Cria a ação do botão de Zoom Out */
        $('.zoom-out').click(function () {
            var val = slider.slider('value') - slider.slider('option', 'step');
            me.changeZoom(val);
        });

        /* Cria a ação do botão de Zoom In */
        $('.zoom-in').click(function () {
            var val = slider.slider('value') + slider.slider('option', 'step');
            me.changeZoom(val);
        });

        $('.aba', '.area-filtros-mapa').tabsControl(this, function(){
            me.update();
        });
    };

    this.toggleFullScreen = function(){
        $('#cabecalho-pagina').slideToggle(500);
        $('#rodape-pagina').slideToggle(500);
        $('#principal .area-site').slideToggle(500);

        if(!fullScreen){
            fullScreen = true;
            
            $('.gmap').animate({height: $(window).innerHeight()-74}, 
                function(){
                    $('.legenda', '.mapa').css('top', $('.gmap').height()-63);
                }
            );

            $(window).resize(function() {$('.gmap').height($(window).innerHeight()-74);});
        }
        else{         
            fullScreen = false;

            $('.gmap').animate({height: mapHeight}, 
                function(){
                    $('.legenda', '.mapa').css('top', $('.gmap').height()-63);
                }
            );
            
            $(window).unbind('resize');
        }

        $('#bt-fullscreen').toggleClass('selecionado');

        
    };

    this.mapLoaded = function () {
		
		

        $('.gmnoprint:first', div).hide();
        $('.container-mapa', div).remove();

        //Esconde a logo do Google no mapa principal
        setTimeout(function () {
            $('img[src="http://maps.gstatic.com/mapfiles/google_white.png"]').parent().remove();
        }, 1000);
    };

    this.changeMapType = function (typeID) {
        $(".maptype", ".mapa .botoes-container").removeClass("selecionado");
        $("#bt-" + typeID).addClass('selecionado');
        map.setMapTypeId(typeID);
    };
    this.changeZoom = function (value) {
        map.setZoom(value);
    },

    this.polygonOver = function () {
        currentPolygonFillColor = this.get('fillColor');
        this.set('fillColor', '#7CC22C');
    };
    this.polygonOut = function () {
        this.set('fillColor', currentPolygonFillColor);
        currentPolygonFillColor = null;
    };
    this.markerClick = function (marker) {

        me.infoWindowClose();

        this.openInfoWindow();
        this.map.panTo(this.getPosition());

        var info = this.getInfoWindow();
        currentInfoWindow = this;

        setTimeout(function () {
            $(".close", info.firstChild).click(function () {
                me.infoWindowClose();
            });
        }, 200);
    };

    this.markerOver = this.markerClick;

    this.markerOut = function () {
        this.closeInfoWindow();
    };

    this.infoWindowClose = function () {

        if (currentInfoWindow != null) {
            currentInfoWindow.closeInfoWindow();
        }
    };

    var clearForm = function (formElement) {
        $('[placeholder]', formElement).qxStylingForms('clear');
        $('.numero', formElement).unsetMask();
    };

    var initForm = function (formElement) {
        $('[placeholder]', formElement).qxStylingForms();
    }

    var getSendData = function (formElement) {
        clearForm(formElement);
        
        $('.numero', formElement).each(function () {
            $(this).val($(this).val().replace(/\./g, '').replace(',', '.'));
        });

        var data = queryStringToObject(formElement.serialize());

        data.view = $("input[name='view']:checked").val();
        data.chart = $("li.ativo a", ".visualizacao-container").attr('href') == "#graficos";
        data.chartType = $("li.ativo a", "#chart-view").attr('href').replace("#", "");

        initForm(formElement);

        if (map) {
            c = map.getCenter() || center;
			if(c)
				data.center = c.lat() + ',' + c.lng();
            data.zoom = map.getZoom();
            data.mapTypeId = map.getMapTypeId();
        }

        return data;
    }

    var loadSource = function (slug, data) {

		

        if (data.chart) {
            if(fullScreen) me.toggleFullScreen();

            $("#map-view").hide();
            $("#chart-view").show();
            me.initChart('/ajax/' + slug + '/chartsource/', data);
        }
        else {

			
			if(slug == 'organization' || $("#filtro-projetos").length==0)
			{
				$(".legenda").hide();
				$("#visualizacao-mapa").hide();
			}else{
				$.ajax({
					url: '/ajax/' + slug + '/mapsource?concentration=1',
					data: data,
					type: 'GET',
					dataType: 'json',
					success: function(response){
						
						var legenda = $(".legenda");

						$(".valor-inicial", legenda).text(response.start);
						$(".valor-final", legenda).text(response.end);
						legenda.show();
						$("#visualizacao-mapa").show();
						


					}
				});
			}
			

            $("#map-view").show();
            $("#chart-view").hide();
			if(center)
			{
				data.center = center.lat() + ',' + center.lng();
			}

			$('div.gmap:visible').initMap('/ajax/' + slug + '/mapsource/', data, ecofundsMap.initMap);
            $('.carregando.tela-mapa', '.mapa').show();
        }
    }

    this.initChart = function (url, data) {

        google.load("visualization", "1", { packages: ["corechart"] });
        //google.setOnLoadCallback(function () {
        $.postCSRF(url, data, function (result) {
            var dt = google.visualization.arrayToDataTable(result);
            //                var formatter = new google.visualization.NumberFormat({
            //                    fractionDigits: 2 //, suffix: '%'
            //                });
            //                formatter.format(data, 1);
            var options = {
                height: 480,
                vAxis: { title: 'Países', titleTextStyle: { color: '#b31d1d'} },
                //hAxis: { format: "#'%'" },
                legend: 'none',
                backgroundColor: { fill: "transparent" },
                colors: [
                    '#B9BFB3',
                    '#93B368',
                    '#4C8038',
                    '#5C9369',
                    '#1C5949',
                    '#3C7179',
                    '#518497',
                    '#5D81A3',
                    '#2B4F6F',
                    '#0A263E'
                ],
            };
            
            var chart;
            if(data.chartType == "bars")
            {
                chart = new google.visualization.BarChart(document.getElementById('chart-content'));
            }
            else
            {
                chart = new google.visualization.PieChart(document.getElementById('chart-content'));
            }
            chart.draw(dt, options);
        }, "json");
        //});
    };
    this.loadDensityProjects = function()
    {
		var data = {};
        data.view = "density";
        data.zoom = 6;
        loadSource('project', data);
    };
	
    this.loadDensityInvestments = function()
    {
		var data = {};
        data.view = "density";
        data.zoom = 6;
        loadSource('investment', data);
    };

    this.loadProjects = function () {
		data = getSendData($("form.projetos"));
        loadSource('project', data);
    };
    this.loadOrganizations = function () {
        data = getSendData($("form.organizacoes"));
        loadSource('organization', data);
    };
    this.loadInvestments = function () {
        data = getSendData($("form.investimentos"));
        loadSource('investment', data);
    };

	

};

var ecofundsMap = new Funbio.Ecofunds.Map();

jQuery(function ($) {

    
    if(document.location.href.indexOf('#filtro-investimentos')>0)
    {
        var from = $("form.projetos");
        var to = $("form.investimentos");
        var fields = ['#id_s_state', '#id_s_country'];

        for(var i = 0; i < fields.length; i++)
        {   
            var fromField = $(fields[i], from);
            var toField = $(fields[i], to);

            
            

            toField.val(fromField.val());
            fromField.val('');
        }
    }

    
    ecofundsMap.init();
	$('.carregando.tela-mapa', '.mapa').show();
    //$('div.gmap:visible').initMap(null, null, ecofundsMap.initMap);    



});






function createProjectSuggest(selector, onSelect) {


	$(selector).suggest({
		url: '/ajax/project/suggest',
		data: { limit: 5 },
		panelClass: 'suggest',
		foundClass: 'encontrado',
		minChars: 3,
		delay: 150,
		onRenderComplete: function (html) {
			$('a', html).attr('href', 'javascript:;').click(function (e) {
				//e.preventDefault();
				//$(selector).keyup();

				if (onSelect) setTimeout(onSelect, 0);
			});

			$(".mais-resultados", html).hide();
		}
	});
}



function createOrganizationSuggest(selector, onSelect) {
	$(selector).suggest({
		url: '/ajax/organization/suggest',
		data: { limit: 5 },
		panelClass: 'suggest',
		foundClass: 'encontrado',
		minChars: 3,
		delay: 150,
		onRenderComplete: function (html) {
			$('a', html).attr('href', 'javascript:;').click(function (e) {
				//e.preventDefault();
				//$(selector).keyup();

				if (onSelect) onSelect(this);
			});

			$(".mais-resultados", html).hide();
		}
	});
}



function createCountrySuggest(selector, onSelect) {
	$(selector).suggest({
		url: '/ajax/project/countries',
		data: { limit: 5 },
		panelClass: 'suggest',
		foundClass: 'encontrado',
		minChars: 3,
		delay: 150,
		onRenderComplete: function (html) {
			if (onSelect)
				$('a', html).click(function () {
					onSelect(this);
				});
		}
	});
}

function createRegionSuggest(selector, onSelect) {
	$(selector).suggest({
		url: '/ajax/project/regions',
		data: { limit: 5 },
		panelClass: 'suggest',
		foundClass: 'encontrado',
		minChars: 3,
		delay: 150,
		onRenderComplete: function (html) {
			if (onSelect)
				$('a', html).click(function () {
					onSelect(this);
				});
		}
	});
}
