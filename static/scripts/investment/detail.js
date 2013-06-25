CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    if (w < 2 * r) r = w / 2;
    if (h < 2 * r) r = h / 2;
    this.beginPath();
    this.moveTo(x + r, y);
    this.arcTo(x + w, y, x + w, y + h, r);
    this.arcTo(x + w, y + h, x, y + h, r);
    this.arcTo(x, y + h, x, y, r);
    this.arcTo(x, y, x + w, y, r);
    this.closePath();
    return this;
}

var InvestmentFlow = function () {
    var me = this;

    var labelType, useGradients, nativeTextSupport, animate;

    var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
    //I'm setting this based on the fact that ExCanvas provides text support for IE
    //and that as of today iPhone/iPad current text support is lame
    labelType = (!nativeCanvasSupport || (textSupport && !iStuff)) ? 'Native' : 'HTML';
    nativeTextSupport = labelType == 'Native';
    useGradients = nativeCanvasSupport;
    animate = !(iStuff || !nativeCanvasSupport);

    var Log = {
        elem: false,
        write: function (text) {

        }
    };
    this.isLoaded = false;
    this.init = function () {
        //init data

        $.postCSRF("/ajax/investment/flowsource/" + $("input[name='id']").val() + "/", null, function (json) {
            me.loadComplete(json);
        }, 'json');
    };

    this.loadComplete = function (json) {

        var arr = json.children, len = arr.length;
        for (var i = 0; i < len; i++) {
            //split half left orientation
            if (i < len / 2) {
                arr[i].data.$orn = 'left';
                $jit.json.each(arr[i], function (n) {
                    n.data.$orn = 'left';
                });
            } else {
                //half right
                arr[i].data.$orn = 'right';
                $jit.json.each(arr[i], function (n) {
                    n.data.$orn = 'right';
                });
            }
        }

        //end
        //init Spacetree
        //Create a new ST instance
        me.isLoaded = true;

        $jit.ST.Plot.EdgeTypes.implement({
            'arrow-bezier': {
                'render': function (adj, canvas) {
                    var orn = this.getOrientation(adj),
                        node = adj.nodeFrom,
                        child = adj.nodeTo,
                        dim = adj.getData('dim'),
                        from = this.viz.geom.getEdge(node, 'begin', orn),
                        to = this.viz.geom.getEdge(child, 'end', orn),
                        direction = adj.data.$direction,
                        swap = (direction && direction.length > 1 && direction[0] != node.id);

                    var ctx = canvas.getCtx();
                    // invert edge direction
                    if (swap) {
                        var tmp = from;
                        from = to;
                        to = tmp;
                    }
                    var vect = new $jit.Complex(to.x - from.x, to.y - from.y);
                    vect.$scale((dim - 3) / vect.norm());
                    var intermediatePoint = new $jit.Complex(to.x - vect.x, to.y - vect.y),
                    normal = new $jit.Complex(-vect.y / 2, vect.x / 2),
                    v1 = intermediatePoint.add(normal),
                    v2 = intermediatePoint.$add(normal.$scale(-1));

                    ctx.beginPath();
                    ctx.moveTo(from.x, from.y);

                    dim += 35;
                    switch (orn) {
                        case "left":
                            ctx.bezierCurveTo(from.x + dim, from.y, to.x - dim, to.y, to.x, to.y);
                            break;
                        case "right":
                            ctx.bezierCurveTo(from.x - dim, from.y, to.x + dim, to.y, to.x, to.y);
                            break;
                        case "bottom":
                            ctx.bezierCurveTo(from.x, from.y + dim, to.x, to.y - dim, to.x, to.y);
                            break;
                        case "top":
                            ctx.bezierCurveTo(from.x, from.y - dim, to.x, to.y + dim, to.x, to.y);
                            break;
                    }

                    //ctx.lineTo(to.x, to.y);
                    ctx.stroke();

                    ctx.beginPath();
                    //ctx.moveTo(v1.x, v1.y);
                    //ctx.lineTo(v2.x, v2.y);

                    ctx.moveTo(to.x - 7, to.y - 9);
                    ctx.lineTo(to.x + 7, to.y - 9);

                    ctx.lineTo(to.x, to.y);
                    ctx.closePath();
                    ctx.fill();
                }
            }
        });

        $jit.ST.Plot.NodeTypes.implement({
            'stroke-rect': {
                'render': function (node, canvas) {

                    var width = node.getData('width');
                    var height = node.getData('height');

                    var pos = this.getAlignedPos(node.pos.getc(true), width, height),
                        posX = pos.x + width / 2,
                        posY = pos.y + height / 2;

                    var ctx = canvas.getCtx();
                    var gradient = ctx.createLinearGradient(pos.x, pos.y + height, pos.x, pos.y);

                    if (node.data.level == 0) {
                        ctx.strokeStyle = '#0B569B';
                        gradient.addColorStop(0, "rgb(12, 87, 156)");
                        gradient.addColorStop(1, "rgb(26, 100, 169)");
                    }
                    else if (node.data.level == 1) {
                        ctx.strokeStyle = '#80A532';
                        gradient.addColorStop(0, "rgb(129, 166, 51)");
                        gradient.addColorStop(1, "rgb(153, 190, 75)");
                    }
                    else {
                        ctx.strokeStyle = '#DCDCDC';
                        gradient.addColorStop(0, "rgb(240, 241, 241)");
                        gradient.addColorStop(1, "rgb(255, 255, 255)");
                    }
                    ctx.lineWidth = 1.2;
                    //ctx.save();
                    ctx.fillStyle = gradient;
                    ctx.fillRect(pos.x, pos.y, width, height);
                    //ctx.restore(); 

                    //this.nodeHelper.rectangle.render('fill', { x: posX, y: posY }, width, height, canvas);
                    this.nodeHelper.rectangle.render('stroke', { x: posX, y: posY }, width, height, canvas);
                }
            }
        });

        var st = new $jit.ST({
            //id of viz container element
            injectInto: 'flow-content',
            orientation: 'bottom',
            //set duration for the animation
            duration: 800,
            //set animation transition type
            transition: $jit.Trans.Quart.easeInOut,
            //set distance between node and its children
            levelDistance: 50,
            //enable panning
            Navigation: {
                enable: true,
                panning: true
            },
            //set node and edge styles
            //set overridable=true for styling individual
            //nodes or edges
            Node: {
                autoHeight: false,
                width: 243,
                height: 53,
                type: 'stroke-rect',
                overridable: true
            },
            Edge: {
                type: 'arrow-bezier',
                overridable: true,
                lineWidth: 2,
                color: '#B2B2B2'
            },

            onBeforeCompute: function (node) {
                
            },

            onAfterCompute: function (node) {

            },

            onBeforePlotNode: function (node) {
                
                if (node.data.level > 1) {
                    node.data.$width = 200
                    node.data.$height = 30
                }
            },
            //This method is called on DOM label creation.
            //Use this method to add event handlers and styles to
            //your node.
            onCreateLabel: function (label, node) {

                label.className = "label " + node.data.css;
                label.id = node.id;
                label.title = node.name;

                var html = "";
                if (node.data.count)
                    html += "<span class=\"count\">" + node.data.count + "</span>";
                html += node.name;

                label.innerHTML = html;

                label.onclick = function () {
                    //if (normal.checked) {
                    st.onClick(node.id);
                    //} else {
                    //st.setRoot(node.id, 'animate');
                    //}
                };
                //set label styles
                var style = label.style;
                style.cursor = 'pointer';
                style.textAlign = 'center';

                if (node.data.level <= 1) {
                    style.fontSize = '14px';
                    style.lineHeight = '53px';
                    style.padding = '0 10px';
                    style.width = '223px';
                    style.height = '53px';
                }
                else {
                    style.fontSize = '12px';
                    style.lineHeight = '30px';
                    style.padding = '0 10px';
                    style.width = '180px';
                    style.height = '30px';
                }
                style.overflow = 'hidden';
                style.textOverflow = 'ellipsis';
                style.whiteSpace = 'nowrap';
                style.color = '#FFF';

                if (node.data.level > 1) {
                    style.color = '#666';
                }
            },

            onBeforePlotLine: function (adj) {
                adj.data.$direction = "bottom";
                if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                    adj.data.$color = "#0B569B";
                    adj.data.$lineWidth = 2;
                }
                else {
                    delete adj.data.$color;
                    delete adj.data.$lineWidth;
                }
            }
        });

        //load json data
        st.loadJSON(json);
        //compute node positions and layout
        st.compute();
        //optional: make a translation of the tree
        st.geom.translate(new $jit.Complex(-200, 0), "current");
        //emulate a click on the root node.
        st.onClick(st.root);

    };
};
var tabs = null;
(function ($) {
    var flow = new InvestmentFlow();

    $(document).ready(function () {
        //Chama a função que irá desabilitar a seleção do texto.
        $('#flow-content').disableSelection();

        //Monta as abas das fichas. Tem que ser aplicado por ultimo sempre... :( 
        //Por causa do fluxo, continuei usando o jQuery Tabs
/*        tabs = $(".ficha").tabs().bind("tabsselect", function (event, ui) {
            if (ui.index == 1 && !flow.isLoaded) {
                flow.init();
            }
        });
        
        var active = $(".ui-tabs-active", ".ficha");

        if(active.length){
            if(active.find('#ui-id-2').length)
                flow.init();
        }


        if(document.location.href.indexOf('#flow')>0){
            setTimeout(function(){
                $("#ui-id-2").click();
            },1);
        }*/

        tabs = $('.aba', '.menu-abas').tabsControl(this, function(index, element){
            if (index == 1 && !flow.isLoaded) {
                flow.init();
            }            
        });

        var active = $(".ativa", ".ficha");

        if(active.length){
            if(active.find('#id-aba-fluxo').length)
                flow.init();
        }

        if(document.location.href.indexOf('#flow') > 0){
            setTimeout(function(){
                $("#id-aba-fluxo").click();
            }, 1);
        }

    });
})(jQuery);

