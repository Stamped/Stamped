$(document).ready(function() { 

  $('#entry_0').keyup(function() {  
    var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;

    if(!emailReg.test($('#entry_0').val()) || $('#entry_0').val().length == 0) {
      $("#submit").attr("disabled", "disabled");
      $("#submit").removeClass("active");
      return false; 
    }        
    $("#submit").removeAttr("disabled");
    $("#submit").addClass("active"); 
  });
    
  $('#entry_0').focus(function() {
    $('#entry_0_wrapper').addClass('active');
  });
  
  $('#entry_0').blur(function() {
    $('#entry_0_wrapper').removeClass('active');
  });
  
  $("#submit").mousedown(function() {
    $("#submit").addClass('pressed')
  });
  
  $("#submit").mouseup(function() {
    $("#submit").removeClass('pressed')
  });
  
  $("#submit").mouseleave(function() {
    $("#submit").removeClass('pressed')
  });
  
  $("#submit").attr("disabled", "disabled");
  
  $("#main-container").fadeIn(500);
  
  $('#submit').click(function() {
    var data = "entry.0.single=" + encodeURIComponent($("#entry_0").val());
    $("#main-container").append("<div id=\"thanks\">Whoa. Thanks!</div>");
    $("#form").fadeOut(250, function() {
      $("#thanks").fadeIn(250);
      $.ajax({
        url: "https://spreadsheets.google.com/a/stamped.com/spreadsheet/formResponse?formkey=dGFzSUpKR3l3NEJMVmM2QlVYbS1UbGc6MQ&amp;ifq",
        type: "POST",
        data: data
      });
    });
    return false;
  });
  
});
