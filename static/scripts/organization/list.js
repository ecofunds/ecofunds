/// <reference path="../reference.js" />
/// <reference path="../global/list.js" />

$(document).ready(function () {

	var getData = function () {


		var from = $("input[name='s_estimated_investments_value_from']");
		var to = $("input[name='s_estimated_investments_value_to']");

		if (from.length && to.length) {

			if (Number(from.val().replace(',', '')) == 0 && Number(to.val().replace(',', '')) == 0) {
				from.val(''); to.val('');
			}
			else {
				from.val(from.val().replace(/\./g, '').replace(',', '.'));
				to.val(to.val().replace(/\./g, '').replace(',', '.'));
			}
		}
		return queryStringToObject($(".form-filtros").serialize());
	};


	showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), true);

	initForm();
	dispatchListEvents(getData);
	dispatchFilterEvents(getData);

	showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), false);

});
