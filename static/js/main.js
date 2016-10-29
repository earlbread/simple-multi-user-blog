/* main.js */

/* Add event listener for confirming when delete button is clicked */
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

/* Add event listener for changing tag when comment edit button is clicked */
(function() {
  var edit_comment_buttons = document.querySelectorAll('.btn-edit-comment');

  edit_comment_buttons.forEach(function(element) {
    element.addEventListener('click', function(event) {
      content_class = '.comment-content-' + this.id;
      edit_form_id = '#comment-edit-' + this.id;

      content_elem = document.querySelector(content_class);
      content_elem.style.display = "none";

      edit_form_elem = document.querySelector(edit_form_id);
      edit_form_elem.style.display = "block";
    });
  });
})();

/* Add event listener for changing tag when comment cancel button is clicked */
(function() {
  var cancel_comment_buttons = document.querySelectorAll('.btn-cancel-comment');

  cancel_comment_buttons.forEach(function(element) {
    element.addEventListener('click', function(event) {
      content_class = '.comment-content-' + this.id;
      edit_form_id = '#comment-edit-' + this.id;

      content_elem = document.querySelector(content_class);
      content_elem.style.display = "block";

      edit_form_elem = document.querySelector(edit_form_id);
      edit_form_elem.style.display = "none";
    });
  });
})();
