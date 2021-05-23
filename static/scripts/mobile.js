(function() {
  if (/webOS|iPhone|iPad|BlackBerry|Windows Phone|Android|Opera Mini/i.test(navigator.userAgent)) {
    $("body, html").css({
      "overflow" : "hidden",
      "height" : "100%"
    });
    $("#main-content").css("height", "100%");
    $(function() {
      $("input").focus(function() {
        window.scrollTo(0, 0);
        document.body.scrollTop = 0;
      });
    });
  }
})();
