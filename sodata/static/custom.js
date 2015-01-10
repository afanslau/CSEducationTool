baseURL = document.URL; // This gets the current url. It fixes the issue when there is a www
display_template = "<p>%s</p>";


//One way to preserve the state of the page might be to reload the entire page after every edit...
// Cite: Explanation http://stackoverflow.com/questions/1195440/ajax-back-button-and-dom-updates



// Event handling setup

$("#resource-delete-button").on("click", function(event, deletebutton) {
  console.log("new function is called for deletebutton")
  
  deleteResource(deletebutton);

  event.stopPropogation();
})




function createSubResource() {
  var topic_id = $("#topic-panel").attr("topic-id");
  var url_elem = $("#new-resource-input-url");
  var title_elem = $("#new-resource-input-title");
  var text_elem = $("#new-resource-input-text");

  var data = {};
  var has_data = false;
  if (url_elem.length === 1) {
    url = url_elem.val();
    if (url) { 
      data['url'] = url;
      has_data = true;
    }
  }
  if (title_elem.length === 1) {
    title = title_elem.val();
    if (title) {
      data['title'] = title;
      has_data = true;
    }
  }
  if (text_elem.length === 1) {
    text = text_elem.val();
    if (text) {
      data['text'] = text;
      has_data = true;
    }
  }

  //Send the request only if there is data there
  if (has_data) {
    var _url;
    if (topic_id) {
      _url = sprintf('/resources/create/%s', topic_id);
    } else {
      _url = '/resources/create';
    }
    $.post(_url, data, function( outData ) {
      location.reload();
      // $("#resource-list-item-input").remove();
      // $("#resource-list-group").prepend($(outData));
      // $(outData)
    });
  } else {
    $("#resource-list-item-input").remove();
  }

}

function deleteResource(deletebutton) {
  console.log("Old function was called for delete resource ");
  
  var rid = $(deletebutton).attr('resource-id');
  var _url = "/api/resources/delete/".concat(rid);
  $.post(_url, function() {
    //Remove the list item for the resource once it gets deletd
    // $("#resource-list-item-".concat(rid)).remove();
    //Simply reload the page - preserves update through back-button functionality
    location.reload();
  });
}

function addResourceClicked() {

  var markup = '<div id="resource-list-item-input" class="list-group-item"><div class="row"><div id="new-resource-input-list" class="col-xs-12"><input id="new-resource-input-title" type="text" class="form-control" placeholder="Add a title"/><!-- {{}}</input> --><!--<div class="wmd-panel"><div id="wmd-button-bar"></div><textarea class="wmd-input" id="wmd-input"></textarea></div> --><textarea id="new-resource-input-text" type="text" class="form-control" rows="2" placeholder="Add a description"/></textarea><!-- <input id="new-resource-input-text" type="text" class="form-control" placeholder="Add a description"/> --><input id="new-resource-input-url" type="text" class="form-control" placeholder="Add a url"/></div><div class="col-xs-12" style="display:inline;"><button id="new-resource-done-button" class="btn btn-default" onclick="createSubResource()">Done</button><!-- <button id="new-resource-link-topic"  class="btn btn-default" onclick="createSubResource()">Add another resource</button> --></div></div></div>';
  var elem = $(markup);
  $('#resource-list-group').prepend(elem);
  $("#new-resource-input-list input").on("keypress", function(e) {
      if(e.which == 13) {
        //Press enter is the same as pressing done
        $("#new-resource-done-button").trigger( "click" );
      }
    });
    $('#new-resource-input-title').focus();

}


function editClicked() {
  var rid = $("#topic-panel").attr('topic-id');
  if (rid) {

    var existing_title = $("#title-content").text();
    if (!existing_title) {
      existing_title = "";
    }
    $("#title-content").remove();
    var titlefield = $('<input id="edit-title" type="text" class="form-control topic-edit" placeholder="Add a title"/>');
    $("#title-div").append(titlefield);
    titlefield.val(existing_title);
    titlefield.focus();

    //Text is rendered as html, so its value is stored in the html of the div
    var existing_text = $("#text-div").html();
    if (!existing_text) {
      existing_text = "";
    }
    $("#text-div").empty();  //At this point, the text field is rendered as html, so there is no content div
    var textfield = $('<textarea id="edit-text" type="text" class="form-control topic-edit" rows="2" placeholder="Add a description"/>');
    $("#text-div").append(textfield);
    textfield.val(existing_text);

    //Do the same with the url
    var existing_url = $("#url-content a").attr('href');
    if (!existing_url) {
      existing_url = "";
    }
    $("#url-content").remove();
    var urlfield = $('<input id="edit-url" type="text" class="form-control topic-edit" placeholder="Add a url"/>');
    $("#url-div").append(urlfield);
    urlfield.val(existing_url);


    $(".topic-edit").on("keypress", function(event) {
      if(event.which == 13)
      {
        event.preventDefault();
        $("#done-button").trigger("click");
      }
    })
    // var existing_content = existing_title.concat("\n", existing_text, "\n", existing_url);
    // var totalfield = $('<textarea class="form-control topic-edit" rows="4"/>');
    // $("#").append(urlfield);


    var done_button = $('<button id="done-button" class="btn btn-default" onclick="doneClicked()" sytle="display:inline;">Done Editing</button>');
    $("#edit-button").remove();
    $("#edit-button-div").append(done_button);
    done_button.on("click", doneClicked);

  }


}

function doneClicked() {
  console.log("Update resource");
  //Send new data to server to update
  var rid = $("#topic-panel").attr('topic-id');

  console.log("Update resource ".concat(rid.toString()));
  var _url = '/resources/update/'.concat(rid);

  var url_elem = $("#edit-url");
  var title_elem = $("#edit-title");
  var text_elem = $("#edit-text");

  var data = {};
  var has_data = true;
  
  url = url_elem.val();
  data['url'] = url;

  title = title_elem.val();
  if (!title) {
    has_data=false;
  }
  data['title'] = title;

  text = text_elem.val();
  data['text'] = text;

  if (has_data) {
    console.log(data);
    $.post(_url, data, function(rendered_html) {
      $(".topic-content").remove()
      $("#topic-panel").prepend($(rendered_html));
    });

  }

}


// $("#star-toggle").click(function toggleStar() {
//   button = $(this); //span tag
//   rid = button.attr("resource-id");
//   _url = "api/resources/unstar/"+rid;
//   if (button.checked) {
//     button.toggleClass("glyphicon glyphicon-star star-toggle");
//     _url = "api/resources/star/"+rid;
//   } else {
//     button.toggleClass("glyphicon glyphicon-star-empty star-toggle");
//   }
//   $.post(_url);
// });


function toggleStar(button_elem) {

  button = $(button_elem); //input checkbox tag
  var span = $(button.context.labels[0].children[1]);

  console.log("toggleStar " + button.is(":checked"));
  rid = button.attr("resource-id");
  _url = "/api/resources/unstar/"+rid;


  if (button.is(":checked")) {

    
    // var $label = $("label[for='"+button.id+"']");
        // console.log(label);
    // console.log(button.find().id);

    span.toggleClass("glyphicon-star-empty");
    span.toggleClass("glyphicon-star");
    _url = "/api/resources/star/"+rid;
  } else {
    span.toggleClass("glyphicon-star-empty");
    span.toggleClass("glyphicon-star");
    
  }
  console.log(_url);
  $.post(_url);
}

function upvote(button) {
  
  var rid = $(button).attr('resource-id');
  var _url = "/api/resources/upvote/".concat(rid);
  $.post(_url, function() {
    //Remove the list item for the resource once it gets deletd
    // $("#resource-list-item-".concat(rid)).remove();
    //Simply reload the page - preserves update through back-button functionality
    location.reload();
  });
}

function downvote(button) {
  
  var rid = $(button).attr('resource-id');
  var _url = "/api/resources/downvote/".concat(rid);
  $.post(_url, function() {
    //Remove the list item for the resource once it gets deletd
    // $("#resource-list-item-".concat(rid)).remove();
    //Simply reload the page - preserves update through back-button functionality
    location.reload();
  });
}



$('#new-resource-form').click(function (e) {
  e.stopPropagation();
});
$("#new-resource-dropdown-toggle").on("click", function (event) {
  console.log('click handler');
  var form = $("#id_title")[0];
  console.log(form);
  $(form).focus();
});

// $("#new-resource-form textarea").attr("rows",10); //How can I set this in django?

$("new-resource-submit-button").on("click", function(event) {
  var form = $('#new-resource-form');
  var data = form.serialize();
  var _url = form.attr("action");

  $("#new-resource-btn-group").removeClass("open");
  $.post(_url, data, function(return_data) {

  });
});





$("#search-button").on("click",function(event) {
  var search_input = $("#search-input");
  if (search_input.is(":visible")) {

    $("#search-form").submit();

  } else {
    //Expand the search input
    search_input.show(); //sets the visible attr so search_input.is(":visible") === true
    search_input.focus();
  }

});


$(".star-button").on("click",function(event) {
  var sb = $(this)
  var rid = sb.attr("resource-id");
  var uid = $("#logged-in-user").attr("user-id");

  if (uid == 0) {
    alert("You must be logged in to do that!");
    return false;
  }

  var starred = sb.attr("checked");
  var _url = "/api/resources/star/"+rid;
  if (starred) {
    sb.attr("checked",0);
    _url = "/api/resources/unstar/"+rid;
  } else {
    sb.attr("checked",1);  
  }
  sb.toggleClass("glyphicon-star-empty");
  sb.toggleClass("glyphicon-star");
  sb.toggleClass("star-button-empty");
  
  console.log(_url);
  //HOW DO I GET THE USER FROM DJANGO??
  $.post(_url).error(function(xhr){
    console.log(xhr.status);
    sb.toggleClass("glyphicon-star-empty");
    sb.toggleClass("glyphicon-star");
  });
})



// function addResourceInput() {

//   //Append another resource box
//   var newInput = $('<div class="input-group input-group-med" name="resource-input-group"><span class="input-group-btn"><input name="resource-input" type="text" class="form-control" placeholder="Resource"><button name="remove-resource-button" class="btn btn-default" type="button" onclick="removeResourceInput()"><span class="glyphicon glyphicon-remove-sign"></span></button></span></div>');
//   $("#topic-resource-list").append(newInput);
//   newInput.find("input[name='resource-input']").focus();
//   //When the input looses focus, check if it is empty
//   newInput.blur(function () {
//     if ($.trim($(this).val()).length === 0) {
//       removeResourceInput($(this))
//     }
//   });
// }
// function removeResourceInput(elem) {
//   console.log(elem)
//   elem.parents('[name="resource-input-group"]').remove()
// }

// function saveTopicEdits() {
//   var title = $("#topic-title-input").val();
//   var resources_dom = $("#topic-resource-list").find("input[name=resource-input]");
//   console.log(resources_dom);
//   var r = [];
//   for (var i=0; i<resources_dom.length; i++) {
//     r.push($(resources_dom[i]).val());
//   }
//   var data = {'title':title, 'id':'999999', 'resource-list':JSON.stringify(r)};
//   var _url = 'save_topic_edits';
//   $.post(_url, data, function( outData ) {
//     alert('saved!' + outData);
//   });
// }



// //Append an input field for title
// function addTitleInput() {
//     var inputmarkup = '<input id="new-resource-input-title" type="text" class="form-control" placeholder="Add a title"/>';
//     var elem = $(inputmarkup);
//     $('#new-resource-input-list').prepend(elem);
// }

// function addNoteInput() {
//   var inputmarkup = '<input id="new-resource-input-note" type="text" class="form-control" placeholder="Add a note"/>';
//   var elem = $(inputmarkup);
//   $('#new-resource-input-list').append(elem);
// }















// function search_topics()
// {
//   //Search for a school by the text input
//   val = $("#topic-search-input").val();

//   url = sprintf("%ssearch_topics/?term=%s", baseURL, encodeURIComponent(val));
//   $.get(url, function( rawdata ) {
//       //First, remove all data that is there already...
//       //No, each search should really be a different page, not AJAX?
//       var data = JSON.parse(rawdata)
//       results = data["results"]
//       console.log(results)
//       $("#display-results-div").empty()
//       for (var i = 0; i < results.length; i++) {
//         var result = results[i];
//         $("#display-results-div").append(sprintf(
//             display_template,
//             result
//           )
//         );    
//       };
//   });
// }

// function autocompleteSearch()
// {
//   // $("#topic-search-input").autocomplete({
//   //   source: function(request, callback) {
//   //     var searchParam  = request.term;
//   //     url = sprintf("%sall_matching_schools/?term=%s", baseURL, encodeURIComponent(searchParam));
//   //     var response = [];
//   //     $.get(url, function( data ) {
//   //       response = $.map( JSON.parse(data), function( n, i ) {
//   //         return (n["name"]);
//   //       });
//   //       callback(response);
//   //     });
//   //   }
//   // });
//   $("#topic-search-input").keypress(function(e) {
//     if(e.which == 13)
//     {
//       e.preventDefault();
//       if ($(this).val().length > 0) {
//         search_topics();
//       };
//       // $(this).autocomplete('close');
//     }
//   });
// }

// function test() {
//   alert("Test Completed");
// }