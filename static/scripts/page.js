$(function() {
  $("#create-username").keyup(function() {
    if ($(this).val().replace(/[^0-9a-zA-Z_\-.\s]+/, "") != $(this).val()) {
      if (!$(this.parentNode).children(".rel").length) {
        $(this.parentNode).append("<div class='rel'><div class='validity'>Please remove the special characters</div></div>");
      }
    }
    else if ($(this).val().replace(/ /, "") != $(this).val()) {
      if (!$(this.parentNode).children(".rel").length) {
        $(this.parentNode).append("<div class='rel'><div class='validity'>Please remove the spaces</div></div>");
      }
    }
    else {
      $(this.parentNode).find(".rel").each(function(i, item) {
        item.remove();
      });
    }

    $(this).val().length < 4 ? this.setCustomValidity("Please increase the length of your username") : this.setCustomValidity("");
  });

  $(".image-post").dblclick(function() {
    $(event.target.parentNode.parentNode).find(".like-button:visible").each(function(i, item) {
      item.click();
    });
  });


  $("#image-drop").on("dragover", function(e) {
    e.preventDefault();
    e.stopPropagation();
  });

  $("#image-drop").on("dragleave", function(e) {
    e.preventDefault();
    e.stopPropagation();
  });

  $("#image-drop").on("drop", function(e) {
    e.preventDefault();
    e.stopPropagation();
    if (!["image/png", "image/jpeg", "image/gif"].includes(e.originalEvent.dataTransfer.files[0].type)) {
      $(event.target).html("<p>Invalid file type</p>");
    }
    else {
      $("#post-image").prop("files", e.originalEvent.dataTransfer.files);
      $(event.target).html("<p>" + e.originalEvent.dataTransfer.files[0].name + "</p>");
    }
  });

  $("#image-drop").on("click", function() {
    $("#post-image").click();
  });

  $("#post-image").change(function() {
    if (["image/png", "image/jpeg", "image/gif"].includes($(this).get(0).files[0].type)) {
      $("#image-drop").html("<p>" + $(this).get(0).files[0].name + "</p>");
    }
    else {
      $("#post-image").prop("files", null);
      $("#image-drop").html("<p>Invalid file type</p>");
    }
  });
});


$(document).on("click", ".remaining-comments-button", function() {
  $(event.target.parentNode).prev().slideToggle();
});

$(document).on("click", ".delete-post-button", function(e) {
  if (!confirm("Are you sure you want to delete this post?")) {
    e.preventDefault();
  }
});

$(document).on("click", "#hide-followers-list", function() {
  $("#followers-list").html("<p><span id='followers-button' class='p-click'>Show followers</span></p>");
});

$(document).on("click", "#hide-following-list", function() {
  $("#following-list").html("<p><span id='following-button' class='p-click'>Show following</span></p>");
});

$(document).on("click", ".request", function() {
  $("#follow-request input[name='user']").prop("value", $(event.target.parentNode).text().split(" ")[0]);
  $("#follow-request").submit();
  $(event.target.parentNode).remove();
});


$(document).on("click", ".comment-options", function() {
  $(event.target).next().toggle();
});

$(document).on("click", ".delete-comment", function() {
  var shell = $(event.target.parentNode.parentNode.parentNode.parentNode);
  var content = "<form method='POST' action='/comment/delete' class='delete-post-form'>";
  shell.find(".url-hidden-input").each(function(i, item) {
    content += "<input type='hidden' value='" + $(item).val() + "' name='url'>";
  });
  shell.find(".comment-id").each(function(i, item) {
    content += "<input type='hidden' value='" + $(item).html() + "' name='commentid'>";
  });
  shell.find(".post-id").each(function(i, item) {
    content += "<input type='hidden' value='" + $(item).html() + "' name='id'>";
  });
  shell.append(content + "</form>");
  $(shell).find(".delete-post-form").each(function(i, item) {
    item.submit();
  });
});

$(document).on("click", ".edit-comment", function() {
  $(event.target.parentNode).toggle();
  var shell = $(event.target.parentNode.parentNode.parentNode.parentNode);
  if (!shell.children(".edit-comment-form").length) {
    var content = "<form method='POST' action='/comment/edit' class='edit-comment-form'><input type='hidden' class='previous-val' value='" + shell.children("p").html()  + "'><input required type='text' name='comment' maxlength='100' autocomplete='off' value='" + shell.children("p").html() + "'><p><input type='submit' value='Update' class='accept-button left'> <input type='button' class='close-comment-editor deny-button left' value='Close'></p>";
    shell.find(".url-hidden-input").each(function(i, item) {
      content += "<input type='hidden' value='" + $(item).val() + "' name='url'>";
    });
    shell.find(".comment-id").each(function(i, item) {
      content += "<input type='hidden' value='" + $(item).html() + "' name='commentid'>";
    });
    shell.find(".post-id").each(function(i, item) {
      content += "<input type='hidden' value='" + $(item).html() + "' name='id'>";
    });
    shell.append(content + "</form>")
    shell.children("p").remove();
  }
});

$(document).on("click", ".close-comment-editor", function() {
  var val;
  $(event.target.parentNode.parentNode).find(".previous-val").each(function(i, item) {
    val = $(item).prop("value");
  });
  $(event.target.parentNode.parentNode.parentNode).append("<p>" + val + "</p>");
  $(event.target.parentNode.parentNode).remove();
});

$(document).on("click", ".request-append", function() {
  $("#follow-request input[type='text']").prop("value", $(event.target.parentNode).text().slice(0, $(event.target.parentNode).text().length - 7));
  $("#follow-request").submit();
  $("#users").html("");
});

$("#people").ready(function() {
  $("#follow-request input[type='text']").on("input", function() {
    $("#users").html("");
    if ($(this).val().length > 2) {
      var message = $(this).val().split()[$(this).val().split().length - 1];
      if (message) {
        people.forEach(function(item) {
          if (item.slice(0, message.length) == message) {
            $("#users").append("<p><a href='/people/" + item + "' class='hide-link'><strong>" + item.slice(0, message.length) + "</strong>" + item.slice(message.length, item.length) + "</a><span class='accept-button request-append' style='font-size: 12px;'>Request</span></p>");
          }
        });
      }
    }
  });
});
