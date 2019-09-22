/* When user clicks "like" icon, send a AJAX request
to update database and get back a JSON object with
an updated total like count*/
$(document).ready(function () {
    $('.form-like').on('submit', function (e) {
        var this1 = this
        e.preventDefault()
        var url = $(this).attr('action')
        var spanId = url.split('/').join('')
        var errorId = spanId.replace('like','error')
        var formId = url.replace('/', '').replace('/like', 'form-unlike')

        $.ajax({
            type: "POST",
            url: url,
        })
        .done(function (data) {
            if (data.error) {
                $('#' + errorId).text(data.error)
            } else {
                $('#' + spanId).text(' ' + data.success)
            }

            $(this1).css('display', 'none')
            $('#' + formId).css('display', 'inline-block')
        })
        .fail(() => {
            $('#' + errorId).text("An error has occured")
        })
    })
    $('.form-unlike').on('submit', function (e) {
        var this1 = this
        e.preventDefault()
        var url = $(this).attr('action')
        var spanId = url.split('/').join('').replace('un','')
        var errorId = spanId.replace('like', 'error')
        var formId = url.replace('/', '').replace('/unlike', 'form-like')

        $.ajax({
            type: "POST",
            url: url,
        })
        .done(function (data) {
            if (data.error) {
                $('#' + errorId).text(data.error)
            } else {
                $('#' + spanId).text(' ' + data.success)
            }
            $(this1).css('display', 'none')
            $('#' + formId).css('display', 'inline-block')
        })
        .fail(() => {
            $('#' + errorId).text("An error has occured")
        })
    })
})
