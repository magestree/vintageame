$('#submit_price_filter').on('click', function () {
    $(this).closest("form").submit();
});

categoria_id = $('#categoria_id').attr('class');

// Filter by Price
//----------------------------------------//
$.ajax({
    url: "/get-edge-prices/"+categoria_id,
    type: "GET",

    success: function (json) {
        var min_price = parseInt(json.min_price);
        var max_price = parseInt(json.max_price);
        var min_price_session = parseInt(json.min_price_session);
        var max_price_session = parseInt(json.max_price_session);

        $("#precio_minimo_order_by").val(min_price_session);
        $("#precio_maximo_order_by").val(max_price_session);

        $("#slider-range2").slider({
            range: true,
            min: min_price,
            max: max_price,
            values: [min_price_session, max_price_session],
            slide: function (event, ui) {
                event = event;
                $("#amount2").val("€" + ui.values[0] + " - €" + ui.values[1]);
            }
        });
        $("#amount2").val("€" + $("#slider-range2").slider("values", 0) + " - €" + $("#slider-range2").slider("values", 1));
    }
});

// Definición del orden de productos
$('#select_order_by').on('change', function () {
    $('#form_order_by').submit();
    // var target = $(this).children('option:selected').val();
    // if (target == 'descuentos') {
    //     window.location.href = '/descuentos/';
    // }
    // else {
    //     if (target == 'mejor_valorados') {
    //         window.location.href = '/mejor_valorados/'
    //     }
    // }
});