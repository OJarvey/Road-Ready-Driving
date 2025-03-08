$(document).ready(function () {
    var stripePublicKey = $('#stripe-public-key').text().trim();
    var clientSecret = $('#client-secret').text().trim();
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();

    var style = {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
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
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
            errorDiv.html(html);
        } else {
            errorDiv.text('');
        }
    });

    var form = $('#payment-form');
    var submitButton = $('#submit-button');

    form.on('submit', function (ev) {
        ev.preventDefault();
        card.update({ 'disabled': true });
        submitButton.attr('disabled', true);

        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
            }
        }).then(function (result) {
            if (result.error) {
                var errorDiv = $('#card-errors');
                var html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>
                `;
                errorDiv.html(html);
                card.update({ 'disabled': false });
                submitButton.attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    $.ajax({
                        type: "POST",
                        url: "/checkout/save-order/",
                        headers: {
                            "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()
                        },
                        data: JSON.stringify({
                            full_name: $('#id_full_name').val(),
                            email: $('#id_email').val(),
                            phone_number: $('#id_phone_number').val(),
                            street_address1: $('#id_street_address1').val(),
                            street_address2: $('#id_street_address2').val(),
                            town_or_city: $('#id_town_or_city').val(),
                            county: $('#id_county').val(),
                            postcode: $('#id_postcode').val(),
                            country: $('#id_country').val(),
                            payment_intent_id: result.paymentIntent.id  // Pass Stripe payment intent ID
                        }),
                        contentType: "application/json",
                        success: function (data) {
                            if (data.success) {
                                window.location.href = "/checkout/success/" + data.order_number + "/";
                            } else {
                                $('#card-errors').html("Error saving order: " + (data.error || "Unknown error"));
                                submitButton.attr('disabled', false);
                                card.update({ 'disabled': false });
                            }
                        },
                        error: function () {
                            $('#card-errors').html("Error processing payment.");
                            submitButton.attr('disabled', false);
                            card.update({ 'disabled': false });
                        }
                    });
                }
            }
        });
    });
});