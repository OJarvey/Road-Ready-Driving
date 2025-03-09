$(document).ready(function () {
    var stripePublicKey = $('#stripe-public-key').text().slice(1, -1);
    var clientSecret = $('#client-secret').text().slice(1, -1);
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();

    var style = {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': { color: '#aab7c4' }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };

    var card = elements.create('card', { style: style, hidePostalCode: true });
    card.mount('#card-element');

    card.addEventListener('change', function (event) {
        var errorDiv = $('#card-errors');
        if (event.error) {
            errorDiv.html(`<span class="icon" role="alert"><i class="fas fa-times"></i></span><span>${event.error.message}</span>`);
        } else {
            errorDiv.text('');
        }
    });

    var form = document.getElementById('payment-form');
    var submitButton = $('#submit-button');

    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        card.update({ 'disabled': true });
        submitButton.attr('disabled', true);
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);

        stripe.confirmCardPayment(clientSecret, {
            payment_method: { card: card }
        }).then(function (result) {
            if (result.error) {
                var errorDiv = $('#card-errors');
                errorDiv.html(`<span class="icon" role="alert"><i class="fas fa-times"></i></span><span>${result.error.message}</span>`);
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                submitButton.attr('disabled', false);
            } else if (result.paymentIntent.status === 'succeeded') {
                // Collect form data
                var formData = {
                    full_name: $('#id_full_name').val() || '',
                    email: $('#id_email').val() || '',
                    phone_number: $('#id_phone_number').val() || '',
                    street_address1: $('#id_street_address1').val() || '',
                    street_address2: $('#id_street_address2').val() || '',
                    town_or_city: $('#id_town_or_city').val() || '',
                    county: $('#id_county').val() || '',
                    postcode: $('#id_postcode').val() || '',
                    country: $('#id_country').val() || '',
                    payment_intent_id: result.paymentIntent.id
                };
                console.log("Sending to save_order:", formData);

                // Send to save_order via AJAX
                $.ajax({
                    type: "POST",
                    url: "/checkout/save-order/",
                    headers: { "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val() },
                    data: JSON.stringify(formData),
                    contentType: "application/json",
                    success: function (data) {
                        console.log("Save order response:", data);
                        if (data.success) {
                            window.location.href = "/checkout/success/" + data.order_number + "/";
                        } else {
                            $('#card-errors').html("Error saving order: " + (data.error || "Unknown error"));
                            card.update({ 'disabled': false });
                            submitButton.attr('disabled', false);
                        }
                    },
                    error: function (xhr, status, error) {
                        console.error("AJAX error:", status, error, xhr.responseText);
                        $('#card-errors').html("Error processing order: " + (xhr.responseText || "Unknown error"));
                        card.update({ 'disabled': false });
                        submitButton.attr('disabled', false);
                    }
                });
            }
        });
    });
});