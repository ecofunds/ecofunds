(function ($) {
    $(document).ready(function () { 
    	//Cria as abas.
        //$('.aba', '.menu-abas').tabsControl();

	    //Chama a função de exclusão da ficha.
	    $('.excluir', '.controles-edicao').each(function(){
	    	var detail = $(this).parents('.ficha');
	    	var typeElement = $('body').attr('id');

	    	typeElement = typeElement.substring(0, typeElement.length - 7);

	    	$(this).deleteElements(detail.attr('data-index'), typeElement, 'detail', detail);
	    });        
    });
})(jQuery);
