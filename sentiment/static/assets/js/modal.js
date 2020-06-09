$.ajaxSetup({
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + $('#auth_token').val());
    }
});

$('#sentimentModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  var sentiment = button.data('sentiment')
  var modal = $(this)
  modal.find('.modal-title').text(sentiment)
  $.ajax({
        url: '/api/sentiment/' +  sentiment + '/config',
        cache: true,
        type: 'GET',
        success: function(response) {
            console.log(response);
            var body = modal.find('.modal-body');
            response.rules.forEach(function(rule) {
                console.log(rule)
                body.append('<h4>' + rule.field + '</h4>')
                body.append('<div class="slider-range" data-lower="'
                        +rule.lower+'" data-upper="'
                        +rule.upper+'" id="' +response.classification.name +'_'+ rule.field +'"></div>')
            });
            $('.slider-range').each(function(i ,slider) {
                sentiment_slider(slider)
            })
        },
        error: function(xhr) {

        }
    });
})

$('#sentimentModal').on('hidden.bs.modal', function (event) {
  $(this).removeData();
  $(this).find('.modal-body').html("")
})