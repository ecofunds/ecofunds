
/* *****************************/
/* qxStylingForms
/* *****************************/
/*
* Fn: qxStylingForms
* Description:  Estilizar campos do tipo "select", "radio" e "checkbox"
*
* Options: 
* *** selectclass:      Classe para os inputs do tipo "select"  (default: selectStyled)
* *** checkclass:       Classe para os inputs do tipo "checkbox" (default: checkStyled)
* *** radioclass:       Classe para os inputs do tipo "radio" (default: radioStyled)
* *** animationspeed:   Velocidade das animações (default: fast)
*
* ToDo:
* *** Adicionar compatibilidade com teclas (top-arrow, bottom-arrow e letra inicial da opção)
* *** Fazer funcionar mesmo em elementos escondidos (caso não consiga pegar a largura do "select", tentar buscar o CSS)
* *** Adicionar classe selecionado pra opção que foi selecionada no select
* *** Fazer funcionar com optiongroup
* *** Colocar comentários em português
* *** Usar "delegate" ao invés de binds nas opções
*/

/* MouseWheel Extension */
(function($){$.event.special.mousewheel={setup:function(){var handler=$.event.special.mousewheel.handler;if($.browser.mozilla)$(this).bind("mousemove.mousewheel",function(event){$.data(this,"mwcursorposdata",{pageX:event.pageX,pageY:event.pageY,clientX:event.clientX,clientY:event.clientY})});if(this.addEventListener)this.addEventListener($.browser.mozilla?"DOMMouseScroll":"mousewheel",handler,false);else this.onmousewheel=handler},teardown:function(){var handler=$.event.special.mousewheel.handler;
$(this).unbind("mousemove.mousewheel");if(this.removeEventListener)this.removeEventListener($.browser.mozilla?"DOMMouseScroll":"mousewheel",handler,false);else this.onmousewheel=function(){};$.removeData(this,"mwcursorposdata")},handler:function(event){var args=Array.prototype.slice.call(arguments,1);event=$.event.fix(event||window.event);$.extend(event,$.data(this,"mwcursorposdata")||{});var delta=0,returnValue=true;if(event.wheelDelta)delta=event.wheelDelta/120;if(event.detail)delta=-event.detail/
3;if($.browser.opera)delta=-event.wheelDelta;event.data=event.data||{};event.type="mousewheel";args.unshift(delta);args.unshift(event);return $.event.handle.apply(this,args)}};$.fn.extend({mousewheel:function(fn){return fn?this.bind("mousewheel",fn):this.trigger("mousewheel")},unmousewheel:function(fn){return this.unbind("mousewheel",fn)}})})(jQuery);

(function ($) {
    $.fn.qxStylingForms = function (options, callback) {
        //Variáveis
        var _SELF = $(this);
        var action = "default";
        var defaultOptions = {
            width: "auto",
            selectboxClass: "qx-stylingForms-select",
            checkboxClass: "qx-stylingForms-checkbox",
            radioboxClass: "qx-stylingForms-radio",
            focusClass: "qx-stylingForms-focus",
            optionsClass: "qx-stylingForms-options",
			placeholderClass: "qx-stylingForms-placeholder",
            animationSpeed: 100,
            zIndex: "100",
            maxItens: 10,
            sameWidth: false
        };
        if(options == "clear") {
            action = "clear";
        }

        //Opções
        options = $.extend(defaultOptions, options);

        //Limpa qualquer instância anterior
        _SELF.clean = function (_this) {
            var tagName = $(_this).get(0).tagName.toLowerCase();

            switch (tagName) {
                case "select":
                    if ($(_this).next().hasClass(options.selectboxClass))
                        $(_this).show().next().remove();
                    break;
                case "input":
                    if ($(_this).next().hasClass(options.radioboxClass) || $(_this).next().hasClass(options.checkboxClass))
                        $(_this).show().next().remove();
                    if ($(_this).attr('placeholder') && $(_this).attr('placeholder') == $(_this).val())
                        $(_this).val("").removeClass(options.placeholderClass);
                    break;
            };
        };

        if(action == "clear") {
            return $(this).each(function(){
                _SELF.clean($(this));
            });
        }

        //EACH
        $(this).each(function (index) {
            //Variáveis
            var _this = $(this);
            var html = "";
            var optionsHtml = "";
            _this.next = _this.param = _this.selectbox = _this.radiobox = _this.checkbox = null;

            //Parâmetros dinâmicos
            _this.param = {
                tagName: $(_this).get(0).tagName.toLowerCase(),
                type: $(_this).attr('type'),
                index: index,
                width: null
            };

            //Limpa qualquer instância já programada
            _SELF.clean(_this);

            //-> Selectbox
            _this.selectbox = function () {
                //Data
                _this.data('stylingForms', {});

                //Verifica se o select está exibido, previnindo erros
                if(!_this.is(':hidden')) {

                    //Calcula tamanho do select
                    (options.width != "auto") ? _this.param.width = parseInt(options.width) : _this.param.width = parseInt(_this.outerWidth());

                    //Constrói HTML
                    html += '<ul class="' + options.selectboxClass + '" style="position:relative; width:' + _this.param.width + 'px;">';
                        html += '<li class="' + options.focusClass + '"><a class="qx-stylingForms-focus-text" href="javascript:;" style="height: 100%; display: block;">' + _this.children('option:selected').html() + '</a></li>';
                    html += '</ul>';

                    if($('#qx-stylingFormsOptions').length == 0) {
                        $('<div id="qx-stylingFormsOptions" class="qx-stylingForms-options-container" style="position: absolute; z-index:' + options.zIndex + ';"><div id="qx-stylingForms-options-bound"><ul class="qx-stylingForms-options" /></div></div>').appendTo('body').slideUp(0);
                    }
                    
                    //Escreve HTML
                    _this.after(html);
                    _this.next = $(_this).next();
                    _this.optionsElem = $('#qx-stylingFormsOptions');
                    _this.focusElem = $('a', _this.next.children('.' + options.focusClass));
                    _this.boundElem = $('#qx-stylingForms-options-bound');

                    //Verifica se está desabilitado
                    if ($(_this).is('[disabled]'))
                        _this.next.addClass('disabled');

                    //Salva opções
                    _this.data('stylingForms').options = [];
                    $(_this).find('option').each(function (index) {
                        $(this).removeAttr('data-index');
                        if ($(this).text() != '' && !$(this).is('.not')) {
                            $(this).attr('data-index', index);
                            _this.data('stylingForms').options.push({index: index, text: $(this).html()});
                        }
                    });

                    //Salva posição na tela
                    _this.data('stylingForms').position = [_this.next.offset().top,_this.next.offset().left];
                    _this.data('stylingForms').width = _this.next.width();

                    //Ação ao sair
                    _this.onexit = function (others, event) {
                        //Classes
                        _this.data('stylingForms').clicked = "false";
                        _this.next.removeClass('qx-stylingForms-ativo');

                        if(_SELF.is('select')) {
                            _this.optionsElem.stop().slideUp(options.animationSpeed);
                        } 
                        _this.toTrigger = false;
                    };

                    //Ação ao clicar
                    _this.onclick = function () {
                        if(_this.data('stylingForms').options.length != 0 && !_this.is('[disabled]')) {
                            //Classes
                            _this.next.addClass('qx-stylingForms-ativo');

                            //Valores disponíveis
                            html = '';
                            $(_this.data('stylingForms').options).each(function(i, obj){
                                html += '<li data-index="' + obj.index + '"><a href="javascript:;">' + obj.text + '</a></li>';
                            }); $('ul', _this.optionsElem).html(html);

                            _this.data('stylingForms').clicked = "true";

                            //Click nas opções
                            _this.optionsElem.find('li').each(function (index) {
                                $(this).bind('mousedown.stylingForms', function (event) {
                                    var thisIndex = $(this).attr('data-index');
                                    
                                    _this.focusElem.html($('a', this).html());
                                    _this.children('option').each(function () {
                                        if ($(this).attr('data-index') == thisIndex) {
                                            $(this).attr({ selected: 'selected' });
                                            return false;
                                        }
                                    });
                                    _this.toTrigger = true;
                                    _this.trigger('change');
                                    _this.onexit();

                                    event.preventDefault();
                                    event.stopPropagation();
                                });

                                $(this).bind('click.stylingForms', function (event) {
                                    event.stopPropagation();
                                    event.preventDefault();
                                });
                            });

                            //Ação ao rolar mouse
                            _this.optionsElem.bind({
                                mouseover: function () {
                                    _this.optionsElem.addClass('mouseIn');
                                },
                                mouseout: function () {
                                    _this.optionsElem.removeClass('mouseIn');
                                },
                                mousedown: function (event) {
                                    event.stopPropagation();
                                }
                            });

                            $('body').bind('mousewheel.stylingForms', function(event, delta){
                                if (!_this.optionsElem.hasClass('mouseIn')) {
                                    _this.onexit();
                                   $(this).unbind('mousewheel.stylingForms');                          
                                }
                            });                            
                            

                            //Ação ao clicar na página
                            $('html').bind('mousedown.stylingForms', function (event) {
                                _this.onexit();
                                $('html').unbind('mousedown.stylingForms');
                            });

                            //Calcula altura máxima
                            _this.optionsElem.css({'height': 'auto', 'width':'auto'});
                            _this.boundElem.css({'width':'auto', 'height':'auto','overflow':''});
                            if(options.maxItens != null && options.maxItens < $('option:not(.not)', _this).length) {
                                _this.optionsElem.show();
                                _this.boundElem.height( $($('ul', _this.optionsElem).children()[0]).outerHeight() * options.maxItens).css({'overflow-x':'hidden', 'overflow-y': 'scroll'});
                                if(!options.sameWidth)
                                    _this.boundElem.width( _this.boundElem.width() + 20 );
                            }

                            //Verifica largura
                            if(options.sameWidth) {
                                _this.optionsElem.width( _this.next.outerWidth() );
                            }

                            //Posição
                            _this.optionsElem.slideUp(0);
                            _this.optionsElem.css({'top': _this.next.offset().top + _this.next.height(), 'left': _this.next.offset().left/*, width: _this.data('stylingForms').width*/});
                            _this.optionsElem.slideDown(options.animationSpeed);
                        }
                    };

                    //Funcionar as setas
                     _this.next.bind('keydown.stylingForms', function(event){
                        //Seta para cima
                        if(event.keyCode == 38) {
                            var cachedSelectItem = _this.find('option[value="' + _this.val() + '"]');
                            if(cachedSelectItem.prev().length == 0) {
                                return false;
                            } else {
                                cachedSelectItem.removeAttr('selected');
                                cachedSelectItem.prev().attr('selected','selected');
                                _this.toTrigger = true;
                                _this.trigger('change');
                            }

                            event.preventDefault();
                            event.stopPropagation();

                        //Seta para baixo
                        } else if(event.keyCode == 40) {
                            var cachedSelectItem = _this.find('option[value="' + _this.val() + '"]');
                            if(cachedSelectItem.next().length == 0) {
                                return false;
                            } else {
                                cachedSelectItem.removeAttr('selected');
                                cachedSelectItem.next().attr('selected','selected');                            
                                 var selectedItem = _this.children('option:selected');
                                _this.toTrigger = true;
                                _this.trigger('change');
                            }

                            event.preventDefault();
                            event.stopPropagation();
                        }

                    });

                    //Ação ao mudar opção no select original
                    _this.change(function () {
                            var selectedItem = _this.children('option:selected');
                            $('.qx-stylingForms-focus-text', _this.next).html(selectedItem.html());
                    });

                    //Ação ao clicar no select estilizado
                    $('.qx-stylingForms-focus', _this.next).bind('mousedown.stylingForms', function (event) {
                        $('select').not(_this).each(function(){
                            if(typeof $(this).data('stylingForms') != "undefined")
                                $(this).data('stylingForms').clicked = "false";
                        });

                        if(_this.data('stylingForms').clicked == "true")
                            _this.onexit();
                        else
                            _this.onclick();
                        event.stopPropagation();
                    });


                    if ($.browser.msie && ($.browser.version == "7.0" && $.browser.version == "6.0"))
                        _this.next.css({ "display": "inline", "zoom": "1" });
                    else
                        _this.next.css({ "display": "inline-block" });
                    _this.hide();
                }
            };

            //-> Radiobox
            _this.radiobox = function () {
                //Esconde o radio
                if ($.browser.msie && ($.browser.version == "8.0" || $.browser.version == "7.0" || $.browser.version == "6.0"))
                    _this.css({ 'position': 'absolute', 'left': '-99999999px' }); //Hack IE
                else
                    _this.hide();

                //Adiciona HTML
                _this.after('<a href="javascript:;" style="display:inline-block;" class="' + options.radioboxClass + '"></a>');

                //Verifica se está checado
                if (_this.is(':checked'))
                    $(_this).next().addClass('qx-stylingForms-radio-selected');

                //Ação ao alterar
                $(_this).change(function () {
                    $('input[type="radio"][name="' + _this.attr('name') + '"]').next().removeClass('qx-stylingForms-radio-selected');
                    $(_this).next().addClass('qx-stylingForms-radio-selected');
                });

                //Ação ao clicar
                $(_this).next().bind('click', function () {
                    _this.attr('checked', true).trigger('change');
                });				
            };

             //-> Checkbox
            _this.checkbox = function () {
                //Esconde o checkbox
                if ($.browser.msie && ($.browser.version == "8.0" || $.browser.version == "7.0" || $.browser.version == "6.0"))
                    _this.css({ 'position': 'absolute', 'left': '-99999999px' }); //Hack IE
                else
                    _this.hide();

                //Adiciona HTML
                _this.after('<a style="display:inline-block" href="javascript:;" class="' + options.checkboxClass + '"></a>');

                //Verifica se está checado
                if (_this.is(':checked'))
                    $(_this).next().addClass('qx-stylingForms-checkbox-selected');

                //Ação ao alterar
                $(_this).bind('change', function () {
                    if ($(_this).is(':checked'))
                        $(_this).next().addClass('qx-stylingForms-checkbox-selected');
                    else
                        $(_this).next().removeClass('qx-stylingForms-checkbox-selected');
                });

                //Ação ao clicar
                $(_this).next().bind('click', function () {
                    if ($(_this).is(':checked'))
                        $(_this).attr('checked', false).trigger('change');
                    else
                        $(_this).attr('checked', true).trigger('change');
                });
            };

			//-> Placeholder
            _this.placeholder = function () {
				_this.focus(function() {
					if (_this.val() == _this.attr("placeholder"))
						_this.val("").removeClass(options.placeholderClass);
				}).blur(function() {
					if (_this.val() == "" || _this.val() == _this.attr("placeholder"))
						_this.addClass(options.placeholderClass).val(_this.attr("placeholder"))
				}).blur().parents("form").submit(function() {
					$(this).find("[placeholder]").each(function() {
						var _this = $(this);
						if (_this.val() == _this.attr("placeholder"))
							_this.val("")
					});
				});				
			}

            //INIT
            _this.init = function () {
                switch (_this.param.tagName) {
                    case "select":
                        _this.selectbox();
                        break;
                    case "input":
                        if (_this.param.type == "radio")
                            _this.radiobox();
                        else if (_this.param.type == "checkbox")
                            _this.checkbox();
						else if (_this.attr('placeholder'))
							_this.placeholder();
                        break;
					case "textarea":
						if (_this.attr('placeholder'))
							_this.placeholder();
                };
            };

            //Inicialização
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