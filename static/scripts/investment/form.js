(function ($) {
    $(document).ready(function () {
		//Altera o titulo da organizacao investidora de acordo com o que o usuario digitou
        changeTitle($('#id_funding_organization_text'), $('.investidor', '.info-cadastro-preliminar'), "investment");

        //Altera o titulo da organizacao receptora de acordo com o que o usuario digitou
        changeTitle($('#id_recipient_organization_text'), $('.titulo-cadastro', '.info-cadastro-preliminar'), "investment");

        //Exibe os campos ocultos.
        showHiddenFieldsWithRadio($('#id_investor_project_0'), $('#id_investor_project_1'), $('#investor-project-name'));
        showHiddenFieldsWithRadio($('#id_r_project_0'), $('#id_r_project_1'), $('#recepient-project-name'));
    });
})(jQuery);