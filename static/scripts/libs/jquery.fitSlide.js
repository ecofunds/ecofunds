(function($){
     /************
	* Slider Fit
    *
    * ToDo:
    * - Reaplicar o slider quando o usu�rio redimensionar o navegador
    * - Fazer documenta��o das op��es
	* - O n�mero de itens visiveis deve ser divisivel pela largura do envelope
	************/
    $.fn.fitSlider = function(options, callback){
        var _self = this;

        //Op��es
        options = $.extend({
            animateDuration: 400,
            cycleDuration: 5000,
            easing: '',
            listElement: '.slider-item',
            listContainer: '.slider-lista-opcoes',
            containerElement: '.slider-container',
            contentElement: '.slider-conteudo',
            prevElement: '.slider-anterior',
            nextElement: '.slider-proximo',
            arrows: true,
            thumbs: true,
            autoPlay: true,
            selectedSlider: 1,
            onStartSlide: null,
            onEndSlide: null,
			visibleItens: 1,
			itensToSlide: 1,
			disablePrevArrow: false
        }, options);

        $(this).each(function(){
            //Vari�veis
            var _this = this,
            containerElement = $(_this).find(options.containerElement),
            nextElement = $(_this).find(options.nextElement),
            prevElement = $(_this).find(options.prevElement),
            contentElement = $(_this).find(options.contentElement),
            listElement = $(_this).find(options.listElement),
            listContainer = $(_this).find(options.listContainer),
            itemCount = options.thumbs ? $(listElement).length : $(contentElement).length,
            itemWidth = 0,
            containerWidth = 0,
            currentSlider = options.selectedSlider,
            sliderOffset = 0,
            autoPlayTimeout = null;
            
            //Verifica��es
            if(!options.thumbs)
                $(listContainer).remove();
            if(!options.arrows)
                $(nextElement).add(prevElement).remove();

            //Fun��o de c�lculos iniciais
            _this.calc = function(){
				//Envelopa o container para o c�lculo de itens exibidos
				containerElement.wrap('<div class="envelope" />');				
				itemWidth = $(_this).find('.envelope').width() / options.visibleItens;
				
                //Calcula tamanho total do container
                $(contentElement).each(function(i){
                    i++;
                    $(this).width(itemWidth).data('slider-item',i);
                    containerWidth += itemWidth;
                });

                //Seta largura do container
                $(containerElement).width(containerWidth);

                //C�lculos para lista
                $(listElement).each(function(i){
                    i++;
                    if(i == 1)
                        $(this).addClass('slider-item-primeiro');
                    else if(i == itemCount)
                        $(this).addClass('slider-item-ultimo');
                    $(this).data('slider-item',i);
                });
                
                //Adiciona classe no item selecionado
                $(listElement).eq(currentSlider - 1).addClass('slider-item-selecionado').siblings().removeClass('slider-item-selecionado');
            };

            //Fun��o para iniciar autoPlay
            _this.autoPlay = function(){
                //Limpa sess�o
                clearInterval(autoPlayTimeout);

                //Atribui o intervalo
                autoPlayTimeout = setInterval(function(){
                    _this.jumpToSlider('next');
                }, options.cycleDuration);
            };

            //Fun��o para atribuir eventos
            _this.binds = function(){
                //Thumbnails
                if(options.thumbs) {
                    $(listElement).each(function(i){
                        $(this).bind('click', function(){
                            _this.jumpToSlider($(this).data('slider-item'));
                        });
                    });
                }

                //Setas
                if(options.arrows) {
					if (options.disablePrevArrow == true)
						$(prevElement).addClass('desabilitado');
					
                    //Pr�ximo
                    $(nextElement).bind('click', function(){
                       	_this.jumpToSlider('next');
                    });

                    //Anterior
                    $(prevElement).bind('click', function(){
						if (!$(this).hasClass('desabilitado')) {
                        	_this.jumpToSlider('prev');
						}
                    });
                }

                //Autoplay
                if(options.autoPlay) {
                   //Inicializa o autoPlay
                   _this.autoPlay();

                   //Desativa intervalo se o mouse estiver sob o slider
                    $(_this).bind('mouseenter.slider', function(){
                        clearInterval(autoPlayTimeout);
                    });

                    //Ativa novamente ao tirar o mouse do slider
                    $(_this).bind('mouseleave.slider', function(){
                        _this.autoPlay();
                    });
                }
            };

            //Fun��o de movimenta��o do slider
            _this.jumpToSlider = function(sliderNumber){
                //Verifica tipo de sliderNumber
                if(sliderNumber == "next") {				
					if (currentSlider == itemCount || currentSlider + (options.itensToSlide * 1) > itemCount)
						sliderNumber = 1;	
					else						
						sliderNumber = currentSlider + (options.itensToSlide * 1);				
				}
                else if(sliderNumber == "prev")
					if (currentSlider == 1)
						sliderNumber = itemCount + 1 - (options.itensToSlide * 1);
					else
						sliderNumber = currentSlider - (options.itensToSlide * 1);				

                //Anima��o
                $(contentElement).each(function(){
                    if($(this).data('slider-item') == sliderNumber) {

                        //Callback slideStart
                        if (typeof eval(options.onStartSlide) == 'function') {
                            jQuery.fn.callback = options.onStartSlide;
                            _self.callback($(this), options);
                        }

                        //Slider atual
                        currentSlider = sliderNumber;
                        
                        //Busca posi��o
                        var pos = (sliderNumber - 1) * itemWidth * -1;

                        //Adiciona classe de selecionado
                        $(listElement).eq(sliderNumber - 1).addClass('slider-item-selecionado').siblings().removeClass('slider-item-selecionado');
                        $(this).addClass('slider-conteudo-selecionado').siblings().removeClass('slider-conteudo-selecionado');
                                                
                        //Anima��o
                        $(containerElement).animate({'margin-left':pos}, options.animateDuration, options.easing, function(){
                            //Callback slideEnd
                            if (typeof eval(options.onEndSlide) == 'function') {
                                jQuery.fn.callback = options.onEndSlide;
                                _self.callback($(this), options);
                            }
                        });

                        return false;
                    }
                });
            };

            //Fun��o de inicializa��o
            _this.init = function(){
                _this.calc();
                _this.binds();
                _this.jumpToSlider(options.selectedSlider);
            };


            //Inicializa��o
            _this.init();
        });
        
        //Callback
        if (typeof eval(callback) == 'function') {
            jQuery.fn.callback = callback;
            _self.callback();
        }

         //Retorno
         return this;  
    };
})(jQuery);