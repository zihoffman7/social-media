$(function() {
  $(".switch input").change(function() {
    if (!$(this).is("[disabled]")) {
      $(this).attr("disabled", true);
    }
    var fd = new FormData();
    fd.append("public", $(this).prop("checked"));
    $.ajax({
      url: "/status",
      type: "POST",
      data: fd,
      cache: false,
      async: true,
      contentType: false,
      processData: false,
      success: function(data) {
        if (data.message == "true") {
          $("#account-status").html("public&nbsp;");
        }
        else {
          $("#account-status").html("private");
        }
        setTimeout(function() {
          $(".switch input").removeAttr("disabled");
        }, 100);
      },
      error: function(err) {
        alert("There was an error somewhere");
        e.preventDefault();
      }
    });
  });

  $("#register-form").submit(function(e) {
    e.preventDefault();
    var fd1 = new FormData();
    var fd2 = new FormData();
    fd1.append("username", $("input[name='username']").val());
    fd2.append("p1", $("input[name='p1']").val());
    fd2.append("p2", $("input[name='p2']").val());

    Promise.all([
      $.ajax({
        url: "/check/username",
        type: "POST",
        data: fd1,
        cache: false,
        async: true,
        contentType: false,
        processData: false
      }),
      $.ajax({
        url: "/check/passwords",
        type: "POST",
        data: fd2,
        cache: false,
        async: true,
        contentType: false,
        processData: false
      })
    ]).then(function(results) {
      var submittable = true;
      results.forEach(function(item) {
        if (!item.status) {
          submittable = false;
          $("#messages").append("<p>" + item.message + "</p>");
        }
      });
      if (submittable) {
        $("#register-form").unbind("submit").submit()
      }
    });
  });

  $("#follow-request").submit(function(e) {
    e.preventDefault();
    var fd = new FormData();
    fd.append("user", $("input[name='user']").val());

    $.ajax({
      url: "/follow/request",
      type: "POST",
      data: fd,
      cache: false,
      async: true,
      contentType: false,
      processData: false,
      success: function(data) {
        if (data.message) {
          $("#messages").append("<p>" + data.message + "</p>");
          $("#follow-request input[type='text']").val("");
        }
        else if (!data.status) {
          location.reload();
        }
      },
      error: function(err) {
        location.reload();
      }
    });
  });

  $("#change-username-form").submit(function(e) {
    e.preventDefault();
    var fd = new FormData();
    fd.append("username", $("input[name='username']").val());

    Promise.all([
      $.ajax({
        url: "/check/username",
        type: "POST",
        data: fd,
        cache: false,
        async: true,
        contentType: false,
        processData: false
      })
    ]).then(function(results) {
      var submittable = true;
      results.forEach(function(item) {
        if (!item.status) {
          submittable = false;
          $("#messages").append("<p>" + item.message + "</p>");
        }
      });
      if (submittable) {
        $("#change-username-form").unbind("submit").submit()
      }
    });
  });

  $("#change-password-form").submit(function(e) {
    e.preventDefault();
    var fd = new FormData();
    fd.append("p1", $("input[name='p1']").val());
    fd.append("p2", $("input[name='p2']").val());

    Promise.all([
      $.ajax({
        url: "/check/passwords",
        type: "POST",
        data: fd,
        cache: false,
        async: true,
        contentType: false,
        processData: false
      })
    ]).then(function(results) {
      var submittable = true;
      results.forEach(function(item) {
        if (!item.status) {
          submittable = false;
          $("#messages").append("<p>" + item.message + "</p>");
        }
      });
      if (submittable) {
        $("#change-password-form").unbind("submit").submit()
      }
    });
  });
});

$(document).on("click", ".accept", function() {
  var parent = event.target.parentNode;
  var fd = new FormData();
  fd.append("user", event.target.dataset.user);

  $.ajax({
    url: "/follow/accept",
    type: "POST",
    cache: false,
    async: true,
    data: fd,
    contentType: false,
    processData: false,
    success: function(data) {
      if (data.show) {
        $(parent).children("button").remove();
        $(parent).append("<button class='accept accept-button request'>Follow back</button>")
      }
      else {
        $(parent).remove();
      }
    },
    error: function(err) {
      location.reload();
    }
  });
});

$(document).on("click", ".deny", function() {
  var parent = event.target.parentNode;
  var fd = new FormData();
  fd.append("user", event.target.dataset.user);

  $.ajax({
    url: "/follow/deny",
    type: "POST",
    cache: false,
    async: true,
    data: fd,
    contentType: false,
    processData: false,
    success: function(data) {
      parent.remove();
    },
    error: function(err) {
      location.reload();
    }
  });
});

$(document).on("click", ".unrequest", function() {
  var parent = event.target.parentNode;
  var fd = new FormData();
  fd.append("user", event.target.dataset.user);

  $.ajax({
    url: "/follow/unrequest",
    type: "POST",
    cache: false,
    async: true,
    data: fd,
    contentType: false,
    processData: false,
    success: function(data) {
      parent.remove();
    },
    error: function(err) {
      location.reload();
    }
  });
});

$(document).on("click", ".unfollow-button", function() {
  var parent = event.target.parentNode;
  var fd = new FormData();
  fd.append("user", event.target.dataset.user);

  $.ajax({
    url: "/follow/unfollow",
    type: "POST",
    cache: false,
    async: true,
    data: fd,
    contentType: false,
    processData: false,
    success: function(data) {
      parent.remove();
    },
    error: function(err) {
      location.reload();
    }
  });
});


$(document).on("click", ".like-button", function() {
  var parent = event.target.parentNode;
  if (!$(this).is("[data-disabled]")) {
    $(parent).find(".like-button").each(function(i, item) {
      $(item).attr("data-disabled", true);
    });
  }
  else {
    return;
  }
  var fd = new FormData();
  fd.append("id", event.target.dataset.id);

  $.ajax({
    url: "/like",
    type: "POST",
    cache: false,
    async: true,
    data: fd,
    contentType: false,
    processData: false,
    success: function(data) {
      for (child of $(parent).children()) {
        $(child).toggle();
      }
      $(parent).next().html(data.likes);
      $(parent).find(".like-button").each(function(i, item) {
        $(item).removeAttr("data-disabled");
      });
    },
    error: function(err) {
      location.reload();
    }
  });
});

$(document).on("click", "#following-button", function() {
  $.ajax({
    url: "/following",
    type: "GET",
    cache: false,
    async: true,
    contentType: false,
    processData: false,
    success: function(data) {
      if (!data.status) {
        location.reload();
      }

      $("#following-list").html("");
      data.data.forEach(function(item) {
        $("#following-list").append("<p><a class='hide-link' href='people/" + item + "'>" + item + "</a><button class='unfollow-button deny-button' data-user='" + item + "'>Unfollow</button></p>");
      });

      if (data.data.length == 0) {
        $("#following-list").html("You aren't following anyone");
      }

      $("#following-button").parent().remove();

      $("#following-list").append("<p><span class='p-click' id='hide-following-list'>Hide</span></p>");
    },
    error: function(err) {
      location.reload();
    }
  });
});

$(document).on("click", "#followers-button", function() {
  $.ajax({
    url: "/followers",
    type: "GET",
    cache: false,
    async: true,
    contentType: false,
    processData: false,
    success: function(data) {
      if (!data.status) {
        location.reload();
      }

      $("#followers-list").html("");
      data.data.forEach(function(item) {
        $("#followers-list").append("<p><a class='hide-link' href='people/" + item + "'>" + item + "</a></p>");
      });

      if (data.data.length == 0) {
        $("#followers-list").html("<p>Nobody is following you</p>");
      }

      $("#followers-button").parent().remove();

      $("#followers-list").append("<p><span class='p-click' id='hide-followers-list'>Hide</span></p>");
    },
    error: function(err) {
      location.reload();
    }
  });
});
