$(function() {
  $("#slider")
    .slider({
    range: "max",
    min: 1,
    max: 5,
    value: 3,
    slide: function(event,ui){
      $("#amount").val(ui.value);
      var face =  $(".face-wrapper").children();
      
      switch(ui.value){
          
        case 1:
          removeClass();
          $(face).addClass("case1");  
        break;
          
        case 2:
          removeClass();
          $(face).addClass("case2");  
        break;
          
        case 3:
          removeClass();
          $(face).addClass("case3");
        break;
          
        case 4:
          removeClass();
          $(face).addClass("case4");
        break;
          
        case 5:
          removeClass();
          $(face).addClass("case5");
        break; 
      }
    }
    
    
  })
  .slider('pips', {
    first: 'pip',  
    last: 'pip',   
  
});

})




//remove previous case classes
function removeClass(){
  $(".face-wrapper").children().removeAttr('class');
}


  