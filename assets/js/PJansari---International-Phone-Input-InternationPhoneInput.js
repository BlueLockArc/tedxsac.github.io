var input = $("#phone");
var errorMsg = $("#invalid-msg");
var validMsg = $("#valid-msg");

// here, the index maps to the error code returned from getValidationError - see readme
var errorMap = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];

// initialise plugin
var iti = window.intlTelInput(document.querySelector('#phone'), {
  utilsScript: "./utils.js"
});

var reset = function() {
  input.removeClass("error");
  errorMsg.html("");
  errorMsg.addClass("hide");
  validMsg.addClass("hide");
};

// on blur: validate
input.blur(function() {
  reset();
  if (input.val().trim()) {
    if (iti.isValidNumber()) {
      validMsg.removeClass("hide");
        console.log(input);
    } else {
      input.addClass("error");
      var errorCode = iti.getValidationError();
        errorMsg.html(errorMap[errorCode]);
      errorMsg.removeClass("hide");
    }
  }
});

// on keyup / change flag: reset
input.change(reset);
input.keyup(reset);