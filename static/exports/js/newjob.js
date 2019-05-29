$(document).ready(function(){
	$("#submitbtn").on('click', function (event) {  
           var el = $(this);
           el.prop('disabled', true);
           $("#newimport").submit();
     });
});