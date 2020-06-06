$.ajaxSetup({
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + $('#auth_token').val());
    }
});

$(function() {
  $('#slider')
    .slider({
    range: 'max',
    min: 1,
    max: 5,
    value: 3,
    slide: function(event,ui){
      $('#amount').val(ui.value);
      var face =  $('.face-wrapper').children();
      removeClass();
      $(face).addClass('case' + ui.value);
    },

    stop: function( event, ui ) {
          $.ajax({
                url: '/api/sentiment/' +  ui.value + '/playlist',
                cache: true,
                type: 'GET',
                success: function(response) {
                    var src = 'https://open.spotify.com/embed/playlist/' + response['id']
                    $('#slider_spotify_player iframe').attr({'src': src});
                    console.log(response);
                },
                error: function(xhr) {

                }
            });
    }


  })
  .slider('float', {
    labels : ['Denial', 'Anger', 'Depression', 'Bargaining', 'Acceptance']
    }
  );

})

//remove previous case classes
function removeClass(){
  $('.face-wrapper').children().removeAttr('class');
}

function slide_handler(handle) {
    function on_slide(event, ui) {
        $(ui.handle).text(ui.values[ui.handleIndex]);
    };
    return on_slide
}

function sentiment_slider(handle) {
    $(handle).slider({
        range: true,
        min: 0,
        max: 1,
        step: 0.01,
        values: [$(handle).data('lower'),$(handle).data('upper')]
    }).on('slide', slide_handler(handle));
    console.log($(handle).data('lower'))
}

$(function () {
    $('.slider-range').each(function(i ,slider) {
        sentiment_slider(slider)
    }
    )
});
