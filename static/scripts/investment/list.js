/// <reference path="../reference.js" />

$(document).ready(function () {

	var getData = function () {

		var from = $("input[name='s_investment_from']");
		var to = $("input[name='s_investment_to']");

		if (Number(from.val().replace(',', '')) == 0 && Number(to.val().replace(',', '')) == 0) {
			from.val(''); to.val('');
		}
		else {
			from.val(from.val().replace(/\./g, '').replace(',', '.'));
			to.val(to.val().replace(/\./g, '').replace(',', '.'));
		}
		return queryStringToObject($(".form-filtros").serialize());
	};

	showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), true);

	initForm();
	dispatchListEvents(getData);
	dispatchFilterEvents(getData);

	showLoading($('.modos-visualizacao', '.filtros-listas-tabelas'), false);


	$('.titulo, .doador, .receptor, .resumo', '.cartao').dotdotdot();

});
