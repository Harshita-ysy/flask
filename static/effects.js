// static/js/effects.js
document.addEventListener('DOMContentLoaded', function(){
  // enable Bootstrap tooltips if you add any
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (el) {
    return new bootstrap.Tooltip(el);
  });
});