var input = document.querySelector("#phone-input");
var iti = window.intlTelInput(input, {
        // allowDropdown: false,
        autoInsertDialCode: true,
        // autoPlaceholder: "off",
        // dropdownContainer: document.body,
        // excludeCountries: ["us"],
        // formatOnDisplay: false,
        // geoIpLookup: function(callback) {
        //   fetch("https://ipapi.co/json")
        //     .then(function(res) { return res.json(); })
        //     .then(function(data) { callback(data.country_code); })
        //     .catch(function() { callback("us"); });
        // },
        // hiddenInput: "full_number",
        initialCountry: "in",
        // localizedCountries: { 'de': 'Deutschland' },
        nationalMode: false,
        // onlyCountries: ['us', 'gb', 'ch', 'ca', 'do'],
        // placeholderNumberType: "MOBILE",
        // preferredCountries: ['cn', 'jp'],
        separateDialCode: false,
        showFlags: true,
  utilsScript: "assets/js/utils.js",
});

// store the instance variable so we can access it in the console e.g. window.iti.getNumber()
window.iti = iti;