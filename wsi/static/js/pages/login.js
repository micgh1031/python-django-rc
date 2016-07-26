(function ($) {
  'use strict';

  $(document).ready(function ($) {
    // Reveal Login form
    setTimeout(function () {
      $(".fade-in-effect").addClass('in');
    }, 1);


    // Validation and Ajax action
    $("form#login").validate({
      rules: {
        username: {
          required: true
        },

        passwd: {
          required: true
        }
      },

      messages: {
        username: {
          required: 'Please enter your email.'
        },

        passwd: {
          required: 'Please enter your password.'
        }
      },

      // Form Processing via AJAX
      submitHandler: function (form) {
        show_loading_bar(70); // Fill progress bar to 70% (just a given value)

        var opts = {
          "closeButton": true,
          "debug": false,
          "positionClass": "toast-top-full-width",
          "onclick": null,
          "showDuration": "300",
          "hideDuration": "1000",
          "timeOut": "5000",
          "extendedTimeOut": "1000",
          "showEasing": "swing",
          "hideEasing": "linear",
          "showMethod": "fadeIn",
          "hideMethod": "fadeOut"
        };

        $.ajax({
          url: "/login/",
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({
            do_login: true,
            username: $(form).find('#username').eq(0).val(),
            password: $(form).find('#passwd').eq(0).val(),
          }),
          success: function (resp) {
            show_loading_bar({
              delay: .5,
              pct: 100,
              finish: function () {
                // Redirect after successful login page (when progress bar reaches 100%)
                if (resp.success == true) {
                  window.location.href = '/';
                }
                else {
                  toastr.error("You have entered wrong username and password, please try again.", "Invalid Login!", opts);
                }
              }
            });

          }
        });

      }
    });

    // Set Form focus
    $("form#login .form-group:has(.form-control):first .form-control").focus();
  });
})($);
