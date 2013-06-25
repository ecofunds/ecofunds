(function ($) {
	$(document).ready(function () {

		var getData = function () {


			var from = $("input[name='s_investments_from']");
			var to = $("input[name='s_investments_to']");

			if (Number(from.val().replace(',', '')) == 0 && Number(to.val().replace(',', '')) == 0) {
				from.val(''); to.val('');
			} else {
				from.val(from.val().replace(/\./g, '').replace(',', '.'));
				to.val(to.val().replace(/\./g, '').replace(',', '.'));
			}
			return queryStringToObject($(".form-filtros").serialize());

		};

		//Não deixa o loading aparecer na home. Parece que esse script está sendo carregado lá.
		if ($('body').attr('id') != 'home') {
			showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), true);
		}

		initForm();
		dispatchListEvents(getData);
		dispatchFilterEvents(getData);

		//Não deixa o loading aparecer na home. Parece que esse script está sendo carregado lá.
		if ($('body').attr('id') != 'home') {
			showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), false);
		}
	});
})(jQuery);