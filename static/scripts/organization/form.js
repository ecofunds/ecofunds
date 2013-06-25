(function ($) {
    $(document).ready(function () {
        //Altera o titulo da organizacao de acordo com o que o usuario digitou
        changeTitle($('#id_name'), $('.titulo-cadastro', '.info-cadastro-preliminar'));

        //Seleciona e remove a imagem do projeto
        changePicture($('#id_image'));

        showHiddenFieldsWithSelect($('#id_type'), 8, $('#toolkit'));
    });
})(jQuery);

var show