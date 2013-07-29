(function ($) {
    $(document).ready(function () { 
        //Função que desabilita a seleção de texto
        $.fn.disableSelection = function() {
            return this
                .attr('unselectable', 'on')
                .css('user-select', 'none')
                .on('selectstart', false);
        };        

        //Estiliza todos os select do site.
        $('select').qxStylingForms({
            sameWidth: true,
            zIndex: "50"/*,
            onClick: function(){
                $('.qx-stylingForms-options-bound').css('overflow','hidden');
                
                $('.qx-stylingForms-options-bound').jScrollPane({
                    showArrows: true,
                    arrowScrollOnHover: true,
                    verticalDragMinHeight: 20
                });
            } */    
        });

        //Estiliza todos os checkbox do site
        $('input[type="checkbox"]').qxStylingForms();

        //Estiliza todos os checkbox do site
        $('input[type="radio"]').qxStylingForms();

        //Estiliza todos os placeholders.
        $('[placeholder]').qxStylingForms();
        
        //Remove a logo do Google que é exibida no mapa da Home.
        var PID = setInterval(function () {

            var logoGoogle = $('img[src="http://maps.gstatic.com/mapfiles/google_white.png"]');

            if (logoGoogle.length) {
                logoGoogle.parent().fadeOut();

                clearInterval(PID);
            };

        }, 500);

        //RELAÇÕES
        if($('.relacao.resumida').length){
            $('h4', '.relacao.resumida').dotdotdot();
            $('p', '.relacao.resumida').dotdotdot();
        }

        if($('.relacao.completa').length){
            $('p', '.relacao.completa').dotdotdot();
        }

        //Chama o suggest na busca do topo
        $(".texto-busca-topo").suggest({
            url: '/ajax/suggest',
            data: { limit: 5 },
            panelClass: 'suggest',
            foundClass: 'encontrado',
            minChars: 3,
            delay: 150
        });

        //Expande a definicao do faq
        faq();

        //Resultado global - filtra os resultados da busca global
        showTypeResult();


        //tabs($('.aba', '.controle-abas.programas'));
    });
})(jQuery);

/* TROCA DE IDIOMAS */
var Funbio = function () {
    return {
        Ecofunds: function () {

            var me = this;
            this.init = function () {
                $("#idioma").change(function () {
                    window.location = $(this).val();
                });
            };
        }
    };
} ();

jQuery(function ($) {
    var ecofunds = new Funbio.Ecofunds();
    ecofunds.init();
});


/*==============================================================================================================================*/
/* Funções Globais */

/* Funções JAVASCRIPT */
var objectToQueryString = function (obj) {
    var str = "";
    var i = 0;
    for (var k in obj) {
        if (i > 0) str += "&";
        str += encodeURIComponent(k) + "=" + encodeURIComponent(obj[k]);
        i++;
    }
    return str;
};

var queryStringToObject = function (q) {
    var e,
        a = /\+/g,  // Regex for replacing addition symbol with a space
        r = /([^\?&=]+)=?([^&]*)/g,
        d = function (s) { return decodeURIComponent(s.replace(a, " ")); },
        urlParams = {};

    while (e = r.exec(q))
        urlParams[d(e[1])] = d(e[2]);
    return urlParams;
};

//Ativa o modo de visualização
var viewModes = function(element){
    var active = 'ativa';
    var deactive = 'inativa';            
    var modeLink = $(element);

    modeLink.each(function(index, element){
        //Cria as variáveis com os elementos que serão utilizados na função
        var modeLinkParent = $(this).parent();
        var mode = $(this).attr('href');
        var modeElement = $(mode);

        //Aqui verifico se o item atual é o primeiro da lista.
        //Se for eu o deixo visível. E oculto os outros.
        if(index == 0){
            modeLinkParent.addClass(active);
            modeElement.addClass(active);
        }
        else{
            modeLinkParent.addClass(deactive);
            modeElement.addClass(deactive);  
        }

        //Aqui começa a ação da função.
        $(this).click(function(event){
            //Remove o evento padrão do click.
            event.preventDefault();

            var classesIcon = $(this).attr("class").split(/\s/);
            var classToRemove = classesIcon[classesIcon.length - 1];
            var classToAdd = classToRemove.split("-")[0] + "-" + (classToRemove.split("-")[1] == active ? deactive : active);

            $(this).removeClass(classToRemove).addClass(classToAdd);                  

            if(modeLinkParent.hasClass(deactive)){
                classesIcon = modeLinkParent.siblings().children().attr("class").split(/\s/);
                classToRemove = classesIcon[classesIcon.length - 1];
                classToAdd = classToRemove.split("-")[0] + "-" + (classToRemove.split("-")[1] == active ? deactive : active);

                modeLinkParent.siblings().children().removeClass(classToRemove).addClass(classToAdd);

                //Remove a classe ativa dos irmãos do elemento atual e adiciona a classe inativa.
                modeLinkParent.siblings().removeClass(active).addClass(deactive);
                
                //Remove a classe ativa dos irmãos do modo de visualizacao atual e adiciona a classe inativa.
                modeElement.siblings().removeClass(active).addClass(deactive);

                //Remove a classe inativa do pai do elemento atual e adiciona a classe ativa.
                modeLinkParent.removeClass(deactive).addClass(active);

                //Remove a classe inativa do modo de visualizacao e adiciona a classe ativa.
                modeElement.removeClass(deactive).addClass(active);
            }
        });              
    });
};

// Função utilizada para mostrar o loader centralizado na tela, independente da resolução
var showLoading = function(element, show){
    
    //LoadingContainer: elemento em que deve ser inserido o blackout
    var loadingContainer = $(element);
    
    //Verifico se os elementos existem. Senão existirem, crio!
    if($('.loader').length == 0){
        $('<div class="loader"/>').appendTo('body');
    }
    
    if($('.carregando.tela-listagem').length == 0){
        $('<div class="carregando tela-listagem"/>').prependTo(loadingContainer);
    }

    var loader = $('.loader'); //Loader: Div com o elemento "carregando"
    var blackout = $('.carregando.tela-listagem'); //Blackout: Div para colocar uma "cortina" em cima do conteúdo
   
    var passed = false; //Variável verificadora para que o css seja aplicado apenas uma vez
    var offsetPassed = -100; //Valor em pixel para uma margem de segurança (teste com outros valores)
    
    if (show == true){
        //Exibe os elementos para poder fazer todos os cálculos        
        blackout.show();
        loader.show();

        //Calculando posição X do loader (posição x do loadingContainer na tela + o tamanho do loadingContainer divido por 2 para centralizar)
        //Também é preciso tirar metade do tamanho do próprio loader
        loader.css({ left: loadingContainer.offset().left + (loadingContainer.outerWidth() / 2) - (loader.outerWidth() / 2)  });
        
        //Posiciona o loader no meio do y da tela
        if ( ($(window).scrollTop() + $(window).height()) > (loadingContainer.outerHeight() + loadingContainer.offset().top) + offsetPassed ) { //Verifica se o scroll passou do limite
            loader.css({ position: 'absolute', top: (((loadingContainer.outerHeight() + loadingContainer.offset().top) - $(window).scrollTop()) / 2) + $(window).scrollTop()  });
            passed = true;
        } else {
            loader.css({ top: $(window).height() / 2  });
        }

        //Verifica se o loader está "quase" ultrapassando o limite do Container
        $(window).scroll(function(){ //A cada scroll faz a verificação

            console.log('Posição da janela:', ($(window).scrollTop() + $(window).height()) );
            console.log('Posição do loadingContainer:', (loadingContainer.outerHeight() + loadingContainer.offset().top) );

            if ( ($(window).scrollTop() + $(window).height()) > (loadingContainer.outerHeight() + loadingContainer.offset().top) + offsetPassed ) { //Verifica se o scroll passou do limite
                if(passed == false) {
                    loader.css({ position: 'absolute', top: ($(window).height() / 2) + $(window).scrollTop()  });
                    passed = true;
                }
            } 
            else { //Se não, volta ao estado normal
                if(passed == true) {
                    loader.css({ position: 'fixed', top: $(window).height() / 2  });
                    passed = false;
                }
            }

        });

        $(window).trigger('scroll'); //Executa a função quando a página carrega
    }
    else{
        //Oculta os elementos
        blackout.hide();
        loader.hide();

        $(window).unbind('scroll');        
    }

};

//Expande os filtros
//Ver mais/Ver menos nos filtros
var showFilterMap = function(){
    $('.filtros', '.area-filtros-mapa').each(function(){
        var link = $('.ocultar-exibir-filtro', this);
        var filter = $(this);

        filter.removeClass('aberto').addClass('fechado');
        var filterHeightClose = filter.outerHeight();

        filter.removeClass('fechado').addClass('aberto');            
        var filterHeightOpen = filter.outerHeight();

        link.bind(
            'click', function(){
                if (filter.hasClass('aberto')){
                    filter.animate({height: filterHeightClose})
                    filter.removeClass('aberto').addClass('fechado');                               
                }

                else{
                    filter.animate({height: filterHeightOpen});  
                    filter.removeClass('fechado').addClass('aberto');
                }                        
            }
        );                       
    });
}

//Expande a definicao do faq
/* Ver mais/Ver menos nos itens do faq */
var faq = function(){
    if($('.resposta', '.faq-container').length){        
        $('.resposta', '.faq-container').each(function(){
            var linkMais = $('.ler-mais', this);
            var linkMenos = $('.ler-menos', this);

            linkMenos.hide();

            var text = $('.texto-resposta', this);
            var textHeightOpen = text.height();

            text.addClass('fechado');

            var textHeightClose = text.height();
            text.css({height: textHeightClose});

            linkMais.bind('click', function(){
                $(this).hide();
                linkMenos.show();

                text.removeClass('fechado');
                text.animate({height: textHeightOpen});
            });

            linkMenos.bind('click', function(){
                $(this).hide();
                linkMais.show();

                text.animate({height: textHeightClose},function(){
                    text.addClass('fechado');    
                });
            });            
        });
    }
};

//Resultado global - filtra os resultados da busca global de acordo com as categorias: 
//projetos, organizações, investimentos, região
var showTypeResult = function(){
    var typesContainer = $('.ordenacao-tipos .lista','.ordenacao');
    
    $('.item', typesContainer).each(function(){
        var typeLink = $('a', this);
        

        typeLink.click(function(event){
            //Remove o evento padrão do click.
            event.preventDefault();

            var typeElement = $(typeLink.attr('href').replace('#','.'),'.resultado-busca');

            $(this).parent().addClass('atual');
            $(this).parent().siblings().removeClass('atual');

            typeElement.removeClass('inativo').addClass('ativo');
            typeElement.siblings().removeClass('ativo').addClass('inativo');
        });
    });
};

//Cria o estilo dos elementos combo.
var createCombo = function(){
    var element = $('.combo');

    if(element.length){
        element.each(function(){
            $(this).wrap('<span class="seta-input-combo" />');
        });
    }
};

//Altera o título do cadastro enquanto o usuario digita
var changeTitle = function(inputText, title, type, extra){
    var titleText = title.html();
    var aux;

    inputText.keyup(function(a){
        if($(this).val() == ""){
            title.html(titleText);
        }
        else{
            title.html($(this).val());
        }
    });

    if(type == "user"){
        extra.keyup(function(a){
            if(!inputText.val() == ""){
                aux = inputText.val() + " " + $(this).val();
                title.html(aux);
            }
        });
    };

    if(type == "investment"){
        if($(this).parent().siblings('.results_on_deck').length){
            aux = $(this).parent().siblings('.results_on_deck').find('div').clone().find('span').remove().end().text();
            title.html(aux);       
        }

        inputText.focusout(function(){
            aux = $(this).parent().siblings('.results_on_deck').find('div').clone().find('span').remove().end().text();
            title.html(aux);
        });
    };
};

//Função que faz a troca de imagens do perfil.
var changePicture = function(evt){
    var changeButton = $('#change-picture');
    var removeButton = $('#remove-picture');

    var picture = $('#picture');
    
    var idFileInput = evt.attr('id');

    showButtons(true);

    /* Clique do botão CHANGE */
    changeButton.click(function(e){
        evt.trigger('click');
    });

    /* Clique do botão REMOVE */
    removeButton.click(function(e){
        picture.attr('src', picture.attr('data-default'));
        
        evt.val("");

        $(this).hide();
        changeButton.show();
    });

    /* Change do File Input */
    evt.change(function(){
        showImage(document.getElementById(idFileInput).files);
    });

    /* Função que utiliza a leitura de arquivos do javascript para exibir as imagens. */ 
    function showImage(image){
        var element = image[0];

        var reader = new FileReader();

        reader.onload = (function(theFile){
            return function(e) {            
                picture.attr('src', e.target.result);
            };
        })(element);

        reader.readAsDataURL(element);

        showButtons(false);
    };

    /* Exibe ou oculta os botões de acordo com a necessidade do script */
    function showButtons(state){
        if(state == true){
            removeButton.hide();
            changeButton.show();
        }
        else{
            changeButton.hide();            
            removeButton.show();
        }
    };
};

//Exibe os campos ocultos de acordo com a marcacao. 
//Primeiro parametro campo para escolha, terceiro parametro o campo a ser exibido.
//Utiliza RADIO.
var showHiddenFieldsWithRadio = function(selectorTrue, selectorFalse, element){
    element.hide();
    
    if(selectorTrue.is(':checked'))
        element.show();

    selectorTrue.on('change',function(){
        if(selectorTrue.is(':checked'))
            element.show();
    });

    selectorFalse.on('change',function(){
        if(selectorFalse.is(':checked'))
            element.hide();
    }); 
};

//Exibe os campos ocultos de acordo com a seleção no dropbox.
//Primeiro parametro select. Segundo, index de condição verdadeira. Terceiro elemento a ser exibido.
var showHiddenFieldsWithSelect = function(selectorElement, index, element){
    element.hide();

    if(selectorElement.find('option:selected').attr('data-index') == index)
        element.show();

    selectorElement.on('change',function(){
        if(selectorElement.find('option:selected').attr('data-index') == index)
            element.show();
        else
            element.hide();        
    });
};

//Controle de abas (Parâmentro: tabControl - elemento que forma as abas)
$.fn.tabsControl = function(tabs, callback){
    var tab;        //Variável para armazenar a aba.
    var tabLink;    //Variável para armazenar o link da aba.
    var tabContent; //Variável para armazenar o conteúdo da aba.
    
    //Percorre todos os itens com a classe aba.
    $(this).each(function(index, element){
        tabLink = $($(this).children('.link-aba'));
        tabContent = $(tabLink.attr('href')); 
        
        //Aqui exibo o conteúdo o conteúdo do primeiro item.
        if(index == 0){
            showContent($(this), tabContent);
        }

        tabLink.click(function(event){  
            event.preventDefault();
            event.stopPropagation();
            
            tab = $(this).parent('.aba');
            tabContent = $($(this).attr('href'));

            showContent(tab, tabContent);

            if(typeof callback == 'function')
                callback(index, element);            
        });
    });

    //Função privada que atribui as classes e exibe os elementos corretos.
    function showContent(tab, tabContent){
        tab.siblings().removeClass('ativa').addClass('inativa');
        tab.removeClass('inativa').addClass('ativa');

        tabContent.siblings().hide().removeClass('ativo').addClass('inativo');
        tabContent.show().removeClass('inativo').addClass('ativo');
    };

    return this;  
};

//Exclusão de elementos: projetos, organizações, usuarios, investimentos.
$.fn.deleteElements = function(id, typeElement, typeList, parent){
    var ajax = '/ajax/' + typeElement + '/remove?id=' + id

    var btnDelete = $(this);
    var btnCancel = $('.cancelar', parent);
    var btnConfirm = $('.confirmar',parent);
    var btnActive = $('.ativar', parent);

    switch(typeList){
        case 'card':
            btnDelete.on('click', function(){
                $('.faixa-conclusao', parent).hide();
                $('.confirmacao', parent).fadeIn();
            });

            btnCancel.on('click', function(){
                $('.faixa-conclusao', parent).show();
                $('.confirmacao', parent).fadeOut();
            });

            btnConfirm.on('click', function(){
                $.getJSON(ajax, function(data){
                  if(data['status']){
                        $('.faixa-conclusao', parent).hide();
                        $('.confirmacao', parent).fadeOut();
                        $('.excluido', parent).fadeIn();
                    }
                });
            });

            btnActive.on('click', function(){
                $('.faixa-conclusao', parent).show();
                $('.excluido', parent).fadeOut();
            });
            break;

        case 'detail':
            btnDelete.fancybox({
                maxWidth    : 800,
                maxHeight   : 600,
                fitToView   : false,
                width       : '425px',
                autoHeight  : true,
                padding     : 0,
                autoSize    : false,
                closeClick  : false,
                closeBtn    : false,
                openEffect  : 'fade',
                closeEffect : 'fade',
                helpers:  {
                    title:  null
                }
            });


            btnCancel.on('click', function(){
                $.fancybox.close(true);
            });

            btnConfirm.on('click', function(){
                $.getJSON(ajax, function(data){
                  if(data['status']){
                        $.fancybox.close(true);
                        window.location.replace("../");
                    }
                });
            });
            
            break;
    }

    return this;
};
