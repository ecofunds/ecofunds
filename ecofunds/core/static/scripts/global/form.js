(function ($) {
    $(document).ready(function () {
		//Tiro a formatação do campo de valor
		$('.form-cadastro').submit(function(){
			$('.numero').each(function (i,v) {
				$(v).val($(v).val().replace(/\./g, '').replace(',', '.'));
			});
			
			return true; // return false to cancel form action
		});    

        //Aqui escondo uma div vazia desnecessária do suggest.
        if ($('div', '.results_on_deck').text() == ""){
            $('div', '.results_on_deck').hide();
        };	
        	
		//Verifico se existe a classe errorList. Se exister, acrescento a classe erro nos inputs.
		$('.campos-editaveis', '.envolve-campo').each(function(){
			if($(this).has('.errorlist').length){
				$(this).addClass('erro');
			}
		});

    });
})(jQuery);