(function ($) {
    $(document).ready(function () {
    	//Altera o titulo do projeto de acordo com o que o usuario digitou
		changeTitle($('#id_title'), $('.titulo-cadastro', '.info-cadastro-preliminar'));
		
		//Seleciona e remove a imagem do projeto
		changePicture($('#id_image'));

        //Exibe os campos ocultos.
        showHiddenFieldsWithRadio($('#id_category_1'), $('#id_category_0'), $('#projects-in-program'));
        showHiddenFieldsWithRadio($('#id_include_0'), $('#id_include_1'), $('#include-in-program'));		
    });
})(jQuery);
