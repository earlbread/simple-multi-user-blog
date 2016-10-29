/* main.js */

/* Confirm when delete button is clicked */
(function() {
  var delete_buttons = document.querySelectorAll('.btn-delete');

  delete_buttons.forEach(function(element) {
    element.addEventListener('click', function(event) {
      if (!confirm('Are you sure?')) {
        event.preventDefault();
      }
    });
  });
})();
