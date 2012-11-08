$(document).ready(function() {
  $(".favourite-form").submit(function(e) {
    e.preventDefault();
    e.stopPropagation();

    $.post($(this).attr("action"), {packages: window.packages}, function() {
      $(".unfavourite-button").removeClass("hide");
      $(".favourite-button").addClass("hide");
    });
    return false;
  });

  $(".unfavourite-form").submit(function(e) {
    e.preventDefault();
    e.stopPropagation();

    $.post($(this).attr("action"), {packages: window.packages}, function() {
      $(".favourite-button").removeClass("hide");
      $(".unfavourite-button").addClass("hide");
    });
    return false;
  });
});
