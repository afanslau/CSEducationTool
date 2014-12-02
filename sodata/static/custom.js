baseURL = document.URL; // This gets the current url. It fixes the issue when there is a www
display_template = "<p>%s</p>";

autocompleteSearch();

function search_topics()
{
  //Search for a school by the text input
  val = $("#topic-search-input").val();

  url = sprintf("%ssearch_topics/?term=%s", baseURL, encodeURIComponent(val));
  $.get(url, function( rawdata ) {
      //First, remove all data that is there already...
      //No, each search should really be a different page, not AJAX?
      var data = JSON.parse(rawdata)
      results = data["results"]
      console.log(results)
      $("#display-results-div").empty()
      for (var i = 0; i < results.length; i++) {
        var result = results[i];
        $("#display-results-div").append(sprintf(
            display_template,
            result
          )
        );    
      };
  });
}

function autocompleteSearch()
{
  // $("#topic-search-input").autocomplete({
  //   source: function(request, callback) {
  //     var searchParam  = request.term;
  //     url = sprintf("%sall_matching_schools/?term=%s", baseURL, encodeURIComponent(searchParam));
  //     var response = [];
  //     $.get(url, function( data ) {
  //       response = $.map( JSON.parse(data), function( n, i ) {
  //         return (n["name"]);
  //       });
  //       callback(response);
  //     });
  //   }
  // });
  $("#topic-search-input").keypress(function(e) {
    if(e.which == 13)
    {
      e.preventDefault();
      if ($(this).val().length > 0) {
        search_topics();
      };
      // $(this).autocomplete('close');
    }
  });
}

function addResourceInput() {

  

}

function addDescription() {


}
function submitDescription() {

  
}
