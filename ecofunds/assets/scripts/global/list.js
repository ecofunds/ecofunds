(function ($) {
    $(document).ready(function () { 
        //Aplica o dotdotdot
        $('.titulo', '.cartao').dotdotdot();
        $('.resumo', '.cartao').dotdotdot();

        //Coloca os tres pontos nas colunas das tabelas.
        if($('.conteudo-registro.texto-linha').length)
        	$('a', '.conteudo-registro.texto-linha').dotdotdot();

	    //Chama a função de exclusão dos cards.
	    $('.excluir', '.controles-edicao').each(function(){
	    	var card = $(this).parents('.cartao');
	    	var typeElement = $('body').attr('id');

	    	typeElement = typeElement.substring(0, typeElement.length - 1);

	    	$(this).deleteElements(card.attr('data-index'), typeElement, 'card', card);
	    });
    });
})(jQuery);

var currentElement = null;
var timeoutList = null;
var xhrList = null;

var clearForm = function () {
	$('[placeholder]', '.form-filtros').qxStylingForms('clear');
	$('.numero', '.form-filtros').unsetMask();
};

var initForm = function () {
	$('[placeholder]', '.form-filtros').qxStylingForms();
}

var dispatchFilterEvents = function (getDataFunc, callbackEventFunc) {
	$(':text', '.form-filtros').bind('keyup paste', function (event) {
		currentElement = $(this);
		var input = this;
		if (timeoutList) {
			clearTimeout(timeoutList);
			timeoutList = null;
		}
		if (event.which == 13) {
			input.form.page.value = '1';
			postList(getDataFunc, callbackEventFunc);
			event.preventDefault();
		}
		else {
			timeoutList = setTimeout(function () {
				timeoutList = null;
				input.form.page.value = '1';
				postList(getDataFunc, callbackEventFunc);
			}, 1000);
		}
	});
	var contexto = $('.form-filtros');


	var bindSelectAll = function (checkName, textName, hint) {
		return function () {
			var cb = $(checkName, contexto);
			var control = $(textName, contexto);
			if (control.length == 0 || cb.length == 0) {
				console.error('Argumentos inválidos:', checkName, textName);
				return;
			}

			console.log('Binding', cb.get(0), ' (', checkName, ') to ', control.get(0), ' (', textName, ')');
			console.log('Control = ', control.val());
			console.log('Checkbox = ', cb.attr('checked'));

			var checked = false;
			control.each(function () {
				if ($(this).val()) {
					checked = true;
					return false;
				}
			});

			if (checked && control.val() != control.attr('placeholder')) {
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
						this.form.page.value = '1';
						postList(getDataFunc, callbackEventFunc);
						//control.change();
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

	$('select', '.form-filtros').change(function () {
		currentElement = $(this);
		this.form.page.value = '1';
		postList(getDataFunc, callbackEventFunc);
	});


	createProjectSuggest("#id_s_project_name", function () {
		$("#id_s_all_project_name").attr('checked', null).qxStylingForms();

		postList(getDataFunc, callbackEventFunc);

	});
	createOrganizationSuggest("#id_s_organization_name, #id_s_organization", function () {
		$("#id_s_all_organizations").attr('checked', null).qxStylingForms();

		postList(getDataFunc, callbackEventFunc);

	});

	createCountrySuggest("#id_s_country", function () {
		postList(getDataFunc, callbackEventFunc);
	});


	createRegionSuggest("#id_s_state", function () {
		postList(getDataFunc, callbackEventFunc);
	});



};

var dispatchListEvents = function (getDataFunc, callbackEventFunc) {

	$(".item a", ".paginacao").click(function (event) {
		obj = queryStringToObject($(this).attr("href"));
		$("input[name='page']", '.form-filtros').val(obj.page);
		postList(getDataFunc, callbackEventFunc);
		event.preventDefault();
	});

	$(".item a", ".ordenacao").click(function (event) {
		order = $(this).attr("href").replace("#", "");
		$("input[name='order_by']", '.form-filtros').val(order);
		postList(getDataFunc, callbackEventFunc);
		event.preventDefault();
	});
	var order_by = $("input[name='order_by']").val();
	if (order_by != "") {
		$(".item", ".ordenacao").removeClass("atual");
		$(".item a[href='#" + order_by + "']", ".ordenacao").parent().addClass("atual");
	}

	console.log($("#principal .filtros-aplicados .fechar-filtro"));

	$("#principal .filtros-aplicados .fechar-filtro").click(function (event) {
		event.preventDefault();

		var li = $(this).parents(".item");
		var fieldName = li.data("field");


		if (fieldName) {
			console.log('field', $("#id_" + fieldName));
			var field = $("#id_" + fieldName);
			field.val("");

			if (field.get(0).type == 'text')
				field.keyup();
			else
				field.change();

			/*if (timeoutList != null) clearTimeout(timeoutList);
			postList(getDataFunc, callbackEventFunc);*/
		}
	});

	var order_by = $("input[name='order_by']");
	$(".item a", ".item").click(function (event) {
		order_by.val($(this).attr('href').replace('#', ''));
		postList(getDataFunc, callbackEventFunc);
		event.preventDefault();
	});

	// Pega o tipo de visualização escolhido. Se for 1 = listagem / 2 = tabelas
	var list_type = $("input[name='list_type']");
	var list = $('.listagem', $('.modos-visualizacao', '.filtros-listas-tabelas'));
	var table = $('.tabelas', $('.modos-visualizacao', '.filtros-listas-tabelas'));
	var link = $('.link', '.visualizacao');

	link.click(function (event) {
		list_type.val($(this).attr('href').replace('#', '') == 'listagem' ? 1 : 2);
		postList(getDataFunc, callbackEventFunc);
		event.preventDefault();
	});

	if (list_type.val() == 1) {
		/* Listagem */
		list.removeClass('inativo').addClass('ativo');

		/* Tabelas */
		table.removeClass('ativo').addClass('inativo');
	}
	else if (list_type.val() == 2) {
		/* Listagem */
		table.removeClass('inativo').addClass('ativo');

		/* Tabelas */
		list.removeClass('ativo').addClass('inativo');
	}

};
var postList = function (getDataFunc, callback) {



	showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), true);

	clearForm();

	var csrf = $.getCSRF();
	var data = null;

	if ($.isFunction(getDataFunc)) data = getDataFunc();
	else data = {};
	data[csrf.name] = csrf.value;


	//	for (var k in data) {
	//		var v = data[k];
	//		if (typeof v == 'string' && v.indexOf('/')) {
	//			if (v.length == 10)
	//				v = v.split('/').reverse().join('-');
	//			else
	//				v = '';
	//			data[k] = v;
	//		}
	//	}


	return $(".conteudo:first", "#principal").load(
        window.location + ' #principal .conteudo > *', data,
        function (response, status, xhr) {

        	initForm();
        	//Corta os titulos e os resumos dos cartoes.
        	$('.titulo, .doador, .receptor, .resumo', '.cartao').dotdotdot();

        	//Corta os titulos e paragrafos das relacoes.
        	$('h4,p', '.relacao.resumida').dotdotdot();


        	//Coloca os tres pontos nas colunas das tabelas.
        	$('a', '.conteudo-registro.texto-linha').dotdotdot();

        	//Estiliza todos os checkbox do site
        	$('input[type="checkbox"]').qxStylingForms();

        	//Estiliza todos os checkbox do site
        	$('input[type="radio"]').qxStylingForms();


        	dispatchListEvents(getDataFunc, callback);

        	showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), false);

		    //Chama a função de exclusão dos cards.
		    $('.excluir', '.controles-edicao').each(function(){
		    	var card = $(this).parents('.cartao');
		    	var typeElement = $('body').attr('id');

		    	typeElement = typeElement.substring(0, typeElement.length - 1);

		    	$(this).deleteElements(card.attr('data-index'), typeElement, 'card', card);
		    });

        	if ($.isFunction(callback)) callback();
        	//if (currentElement != null) currentElement.focus();

        }
    );
};

$(function () {
	$('.link-destaque').click(function (event) {

		//$('.form-filtros').get(0).reset();

		$('input[type="text"],select', '.form-filtros').val('');
		event.preventDefault();
		$("#id_page").val('1');
		$('select:first', '.form-filtros').change();
	});
});



if (!window.console) {
	window.console = {
		log: function () { },
		warn: function () { },
		error: function () { },
		info: function () { }
	}
}




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
