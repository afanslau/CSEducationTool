baseURL = document.URL; // This gets the current url. It fixes the issue when there is a www
display_template = "<p>%s</p>";

autocompleteSearch();

function addResourceInput() {

  //Append another resource box
  var newInput = $('<div class="input-group input-group-med" name="resource-input-group"><span class="input-group-btn"><input name="resource-input" type="text" class="form-control" placeholder="Resource"><button name="remove-resource-button" class="btn btn-default" type="button" onclick="removeResourceInput()"><span class="glyphicon glyphicon-remove-sign"></span></button></span></div>');
  $("#topic-resource-list").append(newInput);
  newInput.find("input[name='resource-input']").focus();
  //When the input looses focus, check if it is empty
  newInput.blur(function () {
    if ($.trim($(this).val()).length === 0) {
      removeResourceInput($(this))
    }
  });
}
function removeResourceInput(elem) {
  console.log(elem)
  elem.parents('[name="resource-input-group"]').remove()
}

function saveTopicEdits() {
  var title = $("#topic-title-input").val();
  var resources_dom = $("#topic-resource-list").find("input[name=resource-input]");
  console.log(resources_dom);
  var r = [];
  for (var i=0; i<resources_dom.length; i++) {
    r.push($(resources_dom[i]).val());
  }
  var data = {'title':title, 'id':'999999', 'resource-list':JSON.stringify(r)};
  var _url = 'save_topic_edits';
  $.post(_url, data, function( outData ) {
    alert('saved!' + outData);
  });
}

function addDescription() {


}
function submitDescription() {

  
}


function addResourceClicked() {

  var markup = '<div class="list-group-item"><div class="row"><div id="new-resource-input-buttons" class="col-xs-12"><ul><li class="new-resource-input-button-title"><a href="javascript:addTitleInput();">Add a title</a></li><li class="new-resource-input-button-note"><a href="javascript:addNoteInput()">Add a note</a></li><li class="new-resource-input-button-link"><a href="javascript:test()">Link to existing topic</a></li></ul></div><div id="new-resource-input-list" class="col-xs-12"><input id="new-resource-input-url" type="text" class="form-control" placeholder="Paste your resource url here"/><!-- <input id="new-resource-input-title" type="text" class="form-control" placeholder="Add a title"/> --><!-- <input id="new-resource-input-note" type="text" class="form-control" placeholder="Add a note"/> --><button id="new-resource-done-button" class="btn btn-default">Done</button></div></div></div>';
  var elem = $(markup);
  console.log(elem);
  $('#resource-list-group').prepend(elem);

}

//Append an input field for title
function addTitleInput() {
    var inputmarkup = '<input id="new-resource-input-title" type="text" class="form-control" placeholder="Add a title"/>'
    var elem = $(inputmarkup);
    console.log(elem);
    $('#new-resource-input-list').prepend(elem);
}



















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

function test() {
  alert("Test Completed");
}