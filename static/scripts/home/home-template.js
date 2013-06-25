(function ($) {
    $(document).ready(function () { 
        //Aplica o dotdotdot
        $('.titulo', '.cartao').dotdotdot();
        $('.resumo', '.cartao').dotdotdot();

        // Chama Slider do Banner da Home
        $('.slider').fitSlider({
            visibleItens: 1,
            itensToSlide: 1
        });        

        //Chama o Carousel
        $('.ultimos-projetos-container').roundabout({
            btnPrev: '.anterior',
            btnNext: '.proximo',
            shape: 'square',
            minOpacity: 1,
            maxScale: 1,
            minScale: 0.6
        });

        //Dar foco nos cartoes na hora do hover.
        $('.roundabout-moveable-item').hover(
            function () {
                if (!$(this).hasClass('roundabout-in-focus')) {
                    $(this).siblings().addClass('cinza-destaque');
                    $(this).addClass('branco-destaque');
                }
            },

            function () {
                if (!$(this).hasClass('roundabout-in-focus')) {
                    $(this).siblings().removeClass('cinza-destaque');
                    $(this).removeClass('branco-destaque');
                }
            }
        );
    	
    });
})(jQuery);