$(document).ready(function(){
    initSearch();
});

function initSearch() {
    $("#search").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#import_list tbody tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
      });
}
