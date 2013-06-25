$(document).ready(function () {


    $('.resultado-item p').css('max-height', '100px').dotdotdot();   

    var frm = document.searchForm;
    var orderby = $("li a", "#ordenacao");
    if (frm.order_by.value == '')
        frm.order_by.value = '-created_at';
    orderby.click(function (event) {
        event.preventDefault();
        order = $(this).attr("href").replace("#", "");

        frm.order_by.value = order;
        frm.submit();
    });

    if (frm.order_by.value) {

        orderby.each(function () {
            if ($(this).attr('href') == '#' + frm.order_by.value)
                $(this).parent().addClass('atual');
            else
                $(this).parent().removeClass('atual');
        });
    }

    $("li.item a", ".paginacao").click(function (event) {
        event.preventDefault();
        var pag = $(this).attr('href').match(/page=(\d+)$/)[1];

        frm.page.value = pag;
        frm.submit();
    });
    if (frm.search_type.value == '')
        frm.search_type.value = 'PRO';
    var searchTypes = $("a", ".ordenacao-tipos .lista");
    searchTypes.click(function (event) {
        event.preventDefault();

        var searchType = $(this).data('search_type');
        frm.search_type.value = searchType;
        frm.submit();
    });

    var type = frm.search_type.value;

    if (type) {
        searchTypes.each(function () {
            if ($(this).data('search_type') == type) {
                $(this).parent().addClass('atual');
            } else {
                $(this).parent().removeClass('atual');
            }
        });
    }

});