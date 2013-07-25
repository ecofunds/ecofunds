//FIXME!!! this code does not belong here
function destroy_statview() {
    if (typeof(statisticsView) !== 'undefined') {
        statisticsView.current_stat.get('view').remove();
        statisticsView.remove();
    }
};

function show_loading() {
    $.blockUI({ message: '<h1>Carregando Dados</h1><img src="' + MEDIA_URL + 'images/loader.gif" />' +
                         '<br/><br/>' });
}

function hide_loading() {
    $.unblockUI(); 
}
//end

$('body').bind('keydown', 'esc', function() {
    $('.container').focus();
});

$('#priority').bind('keydown', 'esc', function() {
    $('.container').focus();
});

$('#questionnaire').bind('keydown', 'esc', function() {
    $('.container').focus();
});

$('body').bind('keydown', 'o', function() {
    $('#aba-content').click();
});

$('body').bind('keydown', 'c', function() {
    $('#count_trigger').click();
});

$('body').bind('keydown', 'p', function() {
    if ($('#pre_query').attr('style') == "display: none; ") {
        $('#pre_query').fadeIn();

        destroy_statview();
    }
    $('#priority').bind('keydown', 'esc', function() {
        $('.container').focus();
    });
    $('#priority').focus();
});

$('body').bind('keydown', 'q', function() {
    if ($('#pre_query').attr('style') == "display: none; ") {
        $('#pre_query').fadeIn();
        destroy_statview();
    }
    $('#questionnaire').bind('keydown', 'esc', function() {
        $('.container').focus();
    });
   $('#questionnaire').focus();
});

$('body').bind('keydown', 's', function() {
    $('#stats_search').focus();
    $('#stats_search').autocomplete('search', ' ');
    return false;
});

$('body').bind('keydown', 'g', function() {
    if (typeof(stats_view) !== 'undefined') {
        stats_view.repaintArea();
    }
});
