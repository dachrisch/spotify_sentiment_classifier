
function sentiment_slider(handle) {
    $(handle).slider({
        range: true,
        min: 0,
        max: 1,
        step: 0.01,
        values: [$(handle).data('lower'),$(handle).data('upper')],
        orientation: 'horizontal'
    }).slider('float');
    console.log($(handle).data('lower'))
}

$(function () {
    $('.slider-range').each(function(i ,slider) {
        sentiment_slider(slider)
    })
});