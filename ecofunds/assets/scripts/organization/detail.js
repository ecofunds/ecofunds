(function ($) {
    $(document).ready(function () {
        //Cria as abas.
        $('.ficha', '#organization-detail').tabs();

        var postForm = function (url) {
            var csrf = $.getCSRF();
            var form = $('<form method="POST" />').attr('action', url).appendTo('body');
            form.append($('<input type="hidden" name="s_organization_id" />').val($("input[name='id']").val()));
            form.append($('<input type="hidden" name="' + csrf.name + '" value="' + csrf.value + '" />'));
            form.submit();
        }
        $('#bt-projects').click(function (event) {
            event.preventDefault();
            postForm($(this).attr('href'));
        });

        $('#bt-investments').click(function (event) {
            event.preventDefault();
            postForm($(this).attr('href'));
        });
    });
})(jQuery);