(function ($) {
    $(document).ready(function () {

    	//Altera o titulo do usuario de acordo com o que o usuario digitou
		changeTitle($('#id_first_name'), $('.titulo-cadastro', '.info-cadastro-preliminar'), "user", $('#id_last_name'));

		//Seleciona e remove a imagem do projeto
		changePicture($('#id_image'));
    });
})(jQuery);