baseURL = document.URL; // This gets the current url. It fixes the issue when there is a www
display_template = "<p>%s</p>";


//One way to preserve the state of the page might be to reload the entire page after every edit...
// Cite: Explanation http://stackoverflow.com/questions/1195440/ajax-back-button-and-dom-updates




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
  var form = $("#id_title")[0];
  $(form).focus();
});

// $("#new-resource-form textarea").attr("rows",10); //How can I set this in django?

//Submits a new resource to the current topic
$("#new-resource-home-submit-button").on("click", function(event) {
  event.stopPropagation();

  var form = $('#new-resource-form');
  var data = form.serialize();

  console.log(data);

  var _url = "/resources/create";
  $.post(_url, data, function(event) {
    alert('your resource was saved to your home screen');
  });
});
$(".submit-button").on("click", function(event) {
  $("#new-resource-btn-group").removeClass("open");
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
  var sb = $(this);
  var sb_span = sb.find("span")
  var rid = sb.attr("resource-id");
  var uid = $("#logged-in-user").attr("user-id");

  if (uid == 0) {
    alert("You must be logged in to do that!");
    return false;
  }

  var starred = sb.attr("starred");

  var _url = "/api/resources/star/"+rid;
  if (starred == 1) {
    sb.attr("starred",0);
    _url = "/api/resources/unstar/"+rid;
  } else {
    sb.attr("starred",1);  
  }
  sb_span.toggleClass("glyphicon-star-empty");
  sb_span.toggleClass("glyphicon-star");
  sb.toggleClass("star-button-empty");
  
  $.post(_url).error(function(xhr){
    console.log(xhr.status);
    sb_span.toggleClass("glyphicon-star-empty");
    sb_span.toggleClass("glyphicon-star");
    sb.blur();
  });
});


$("#paginate-button").on("click",function(event) {
  var rid = $("#resource-id").attr("resource-id");
  var _url = '/resources/'+rid+'/recommendations';
  var container = $("#recommended-container");
  var next_page = parseInt(container.attr("next-page-number"));
  var data = {'page':next_page};
  $.get(_url, data, function(_html) {
    container.append($(_html));
    container.attr("next-page-number", next_page+1);
    $(this).attr("href", "#"+(next_page+1));
  }).error(function(xhr) {
    console.log(xhr.status);
    console.log("No more pages to display");
    // Remove paginate button
    $(this).clear();
  });
});
 


$(".savetohome-button").on("click", function(event) {
  var rid = $(this).attr("resource-id");
  var _url = "/api/relations/create/" + rid;
  $.post(_url, function(returned_data) {
    alert('Saved to home page');
  });
});

$(".saveto-button").on("click", function(event) {
  //Trigger action to select a destination for a resource to be pinned to

  // Remove the existing popup
  $("#pin-to-popup").remove();

  // Render and GET the new popup template from the server
  // Append it to the document and show
  var rid = $(this).attr("resource-id");
  var _url = "/relations/createform/"+rid;
  $.get(_url, function(html) {
    $("#content-container").append($(html));
    var pinto = $("#pin-to-popup");
    pinto.popup('show');
  });
});




$(".dismiss-button").on("click", function(event) {
  
  var pid = $(this).attr("parent-id");
  var rid = $(this).attr("resource-id");
  var _url = "/api/relations/"+pid+"/delete/"+rid;
  $.post(_url, function(response) {
    console.log(response);
  });
  $("#resource-card-container-"+rid).remove();

})

$("#help_popup").popup({
  transition: '0.3s all 0.1s',
  opacity: 0.3
});


// <script>
// $(document).ready(function () {

//     $('#my_tooltip').popup({
//         type: 'tooltip',
//         vertical: 'top',
//         transition: '0.3s all 0.1s',
//         tooltipanchor: $('#my_tooltip_open')
//     });

// });
// </script>

// $('.confirm-delete').popup({
//     backgroundactive: true,
//     vertical: 'bottom',
//     transition: '0.3s all 0.1s',
// });









// $("#pin-to-popup").popup({
//   transition: '0.3s all 0.1s',
//   scrolllock: true,
//   opacity: 0.7,
//   onclose: function() {
//       $(this).removeAttr("resource-id");
//       $("#results-list").empty();
//     }
// });

// $('#destination-selector-input').keyup(function() {
//   clearTimeout($.data(this, 'timer'));
//   var wait = setTimeout(function() {
//     var searchParam  = $('#destination-selector-input').val();
//     var _url = "/search?simple_search=True&q=" + encodeURIComponent(searchParam);
//     $.get(_url, function(data) {
//       $("#results-list").append(data);
//     });
//   }, 500);
//   $(this).data('timer', wait);
// });


// $("#destination-selector-input").autocomplete({
//   source: function(request, callback) {
//     var searchParam  = request.term;
//     var _url = "/search?simple_search=True&q=" + encodeURIComponent(searchParam);
//     $.get(_url, function( data ) {
//       var response = $.map( JSON.parse(data), function( n, i ) {
//         console.log(" .map function args ");
//         console.log(n);
//         console.log(i);
//         return ({"label":n["id"], "value":n["title"]});
//       });
//       callback(response);
//     });
//   },
//   select: function(event, ui) {
//     var child_id = $("#pin-to-popup").attr("resource-id");
//     pinToTopic(ui.attr("value"), child_id);
//   }
// });
// $("#destination-selector-input").keypress(function(e) {
//   if(e.which == 13)
//   {
//     e.preventDefault();
//     // pinToTopic();
//   }
// });
// function pinToTopic(topic_id, resource_id) {
//   var _url = "/api/relations/"+topic_id+"/create/"+resource_id;
//   console.log("pinToTopic   "+_url);
//   // $.post(_url, display_success_tooltip);
// }

function display_success_tooltip() {
  alert("your action was successful");
}
