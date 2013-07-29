(function ($) {
    $(document).ready(function () {
        //Expande a descrição do projeto
        $('.descricao', '.ficha.projeto').expander({
            slicePoint: 400,
            preserveWords: true,
            widow: 2,
            summaryClass: 'sumario',
            detailClass: 'detalhes',
            expandText: 'Ver mais',
            moreClass: 'ler-mais',
            lessClass: 'ler-menos',
            expandEffect: 'slideDown',
            expandSpeed: 500,
            collapseEffect: 'slideUp',
            collapseSpeed: 500,
            userCollapseText: 'Ver menos'
        });    	
    });
})(jQuery);