(function ($) {
    $(document).ready(function () {

        //Estiliza todos os select do site.
        $('select').qxStylingForms({
            sameWidth: true
        });

        //Estiliza todos os checkbox do site
        $('input[type="checkbox"]').qxStylingForms();

        //Estiliza todos os checkbox do site
        $('input[type="radio"]').qxStylingForms();

        //Cria os input do tipo combo (text/select)
        $('.combo').after('<span class="link-seta"></span>');

        //Cria as mascaras dos campos text
        $('.numero').setMask('decimal');

        //Cria as mascaras dos campos text
        $('.data').setMask('date');

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

        //Chama o suggest na busca do topo
        $(".busca-topo").suggest({
            url: '/ajax/project/suggest',
            data: { limit: 5 },
            panelClass: 'suggest',
            foundClass: 'encontrado',
            minChars: 3,
            delay: 0
        });

        //Estiliza todos os scrolls do site
        $('.scroll-pane').jScrollPane({
            showArrows: true,
            arrowScrollOnHover: true,
            verticalDragMinHeight: 20
        });


        //Expande os filtros
        //Ver mais/Ver menos nos filtros
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
                        filter.removeClass('aberto').addClass('fechado');                               
                        filter.animate({height: filterHeightClose})
                    }

                    else{
                        filter.removeClass('fechado').addClass('aberto');
                        filter.animate({height: filterHeightOpen});  
                    }                        
                }
            );                       
        });

        //Monta as abas dos mapas. Tem que ser aplicado por ultimo sempre... :(
        $(".area-filtros-mapa").tabs();

        //Ativa o modo de visualização dos projetos, organizações e investimentos
        viewModes();


        //Expande a descrição do projeto
        $('.descricao').expander({
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

        //Expande a definicao do faq
        /* Ver mais/Ver menos nos itens do faq */
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


        //Aplica o DOTDOTDOT.
        //HOME
        $('.titulo', '.cartao').dotdotdot();
        $('.resumo', '.cartao').dotdotdot();

        //RELAÇÕES
        $('h4', '.relacao.resumida').dotdotdot();
        $('p', '.relacao.resumida').dotdotdot();
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