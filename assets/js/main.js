function showhide(show = "", hide = "") {
    if (show != "") document.getElementById(show).classList.remove("togglable");
    if (hide != "") document.getElementById(hide).classList.add("togglable");
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function check_email() {
    $("#continue-btn").hide();
    $("#email-loading-icon").show();
    $("#email-alert-box").hide();
    var email = $("#email-input").val();
    await fetch("http://127.0.0.1:5000/check/" + email)
        .then(async (response) => {
            const statusCode = response.status;
            const responseData = await response.json();
            if (statusCode === 200) {
                // Email is proper and doesnt exist in db
                $("#email-check-col").hide();
                $("#register-form-col").show();
            } else if (statusCode === 202) {
                $("#email-alert-box").show();
                $("#email-alert-text").html("Email already registered");
            } else if (statusCode === 520) {
                $("#email-alert-box").show();
                $("#email-alert-text").html(responseData.msg);
                // Handle other status codes as needed
            } else {
                console.log('Unexpected status code:', statusCode);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });

    $("#email-loading-icon").hide();
    $("#continue-btn").show();
}
$(document).on('click touchstart', function () {
    var aloy = $('input[name="int-ext"]:checked').val();
    var payment_type = $('input[name="partial-full"]:checked').val();
    if (aloy) {
        showhide("payment-type-row");
        if (aloy == 1) {
            showhide("regno-row");
            $("#partial-radio-btn").prop("disabled", false);
            $("#regno-input").prop("required", true);
        }
        else if (aloy == 0) {
            showhide("", "regno-row");
            $("#partial-radio-btn").prop("disabled", true);
            $("#partial-radio-btn").prop("checked", false);
            $("#regno-input").prop("required", false);
            showhide("full-pay-label", "partial-pay-label");
        }
    }
    var payment_type = $('input[name="partial-full"]:checked').val();
    if (!payment_type) {
        showhide("", "qr-code-col");
    }
    if (payment_type) {
        showhide("qr-code-col");
        if (payment_type == "partial")
            showhide("partial-pay-label", "full-pay-label");
        else if (payment_type == "full")
            showhide("full-pay-label", "partial-pay-label");
    }
});

async function submit_form() {
    var full_name = $("#name-input").val();
    var email = $("#email-input").val();
    var phone = window.iti.getNumber();
    var aloy = $('input[name="int-ext"]:checked').val();
    var regno = $("#regno-input").val();
    var payment_type = $('input[name="partial-full"]:checked').val();
    var upi_ref_no = $("#upi-ref-input").val();

    if (!full_name || !email || !phone || !aloy || !payment_type || !upi_ref_no) {
        alert("Please fill all the required fields.");

    }
    if (!window.iti.isValidNumber()) {
        $("#name-input")[0].scrollIntoView({ behavior: 'smooth' });
        return;
    }
    if (aloy == "yes" && !regno) {
        alert("Please fill all the required fields.");
        $("#regno-input")[0].scrollIntoView({ behavior: 'smooth' });
        return;
    }
    console.log(full_name, email, phone, aloy, regno, payment_type, upi_ref_no);
    await fetch("http://127.0.0.1:5000/register", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            name: full_name,
            phone: phone,
            aloy: aloy,
            regno: regno,
            payment_type: payment_type,
            upi_ref_no: upi_ref_no
        })
    })
        .then(async (response) => {
            const statusCode = response.status;
            const responseData = await response.json();
            if (statusCode === 200) {
                console.log("Form submitted successfully");
                $("#register-form-col").hide();
                $("#success-col").show();
            } else if (statusCode === 202) {
                console.log("Email already registered");
            } else if (statusCode === 520) {
                alert(responseData.msg);
                // Handle other status codes as needed
            } else {
                console.log('Unexpected status code:', statusCode);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}