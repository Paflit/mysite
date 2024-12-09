$(document).ready(function() {
    $('.menu ul').children().click(function (e) {
        $('a[href="' + window.location.hash + '"]').parents('li').removeClass('active');
        $('a[href="' + e.target.hash + '"]').parents('li').addClass('active');
    })

    $('a[href="' + window.location.hash + '"]').parents('li').addClass('active');
});
