/* jshint esversion: 6 */
/* global $, Stripe */

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

    // Handle real-time validation errors on the card element
    card.addEventListener('change', function (event) {
        var errorDiv = $('#card-errors');
        if (event.error) {
            errorDiv.html(`
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `);
        } else {
            errorDiv.text('');
        }
    });

    // Handle form submission
    var form = document.getElementById('payment-form');
    var submitButton = $('#submit-button');

    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        
        // Disable form elements while processing
        card.update({ 'disabled': true });
        submitButton.attr('disabled', true);
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);

        // Get save_info value
        var saveInfo = $('#id-save-info').is(':checked');

        // First cache checkout data
        $.ajax({
            type: "POST",
            url: "/checkout/cache-checkout-data/",
            headers: {
                "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),
            },
            data: {
                'client_secret': clientSecret,
                'save_info': saveInfo,
            },
            success: function () {
                // Proceed with Stripe payment after successful cache
                stripe.confirmCardPayment(clientSecret, {
                    payment_method: {
                        card: card,
                        billing_details: {
                            name: $.trim(form.full_name.value),
                            phone: $.trim(form.phone_number.value),
                            email: $.trim(form.email.value),
                            address: {
                                line1: $.trim(form.street_address1.value),
                                line2: $.trim(form.street_address2.value),
                                city: $.trim(form.town_or_city.value),
                                country: $.trim(form.country.value),
                                postal_code: $.trim(form.postcode.value),
                                state: $.trim(form.county.value),
                            }
                        }
                    }
                }).then(function (result) {
                    if (result.error) {
                        // Handle payment error
                        var errorDiv = $('#card-errors');
                        errorDiv.html(`
                            <span class="icon" role="alert">
                                <i class="fas fa-times"></i>
                            </span>
                            <span>${result.error.message}</span>
                        `);
                        $('#payment-form').fadeToggle(100);
                        $('#loading-overlay').fadeToggle(100);
                        card.update({ 'disabled': false });
                        submitButton.attr('disabled', false);
                    } else {
                        // Payment succeeded - handle order creation
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

                        // Send order data to save_order endpoint
                        $.ajax({
                            type: "POST",
                            url: "/checkout/save-order/",
                            headers: { 
                                "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val() 
                            },
                            data: JSON.stringify(formData),
                            contentType: "application/json",
                            success: function (data) {
                                if (data.success) {
                                    window.location.href = "/checkout/success/" + data.order_number + "/";
                                } else {
                                    // Handle order save errors
                                    var errorDiv = $('#card-errors');
                                    errorDiv.html(`
                                        <span class="icon" role="alert">
                                            <i class="fas fa-times"></i>
                                        </span>
                                        <span>Order save failed: ${data.error || 'Unknown error'}</span>
                                    `);
                                    card.update({ 'disabled': false });
                                    submitButton.attr('disabled', false);
                                }
                            },
                            error: function (xhr, status, error) {
                                // Handle AJAX errors
                                var errorDiv = $('#card-errors');
                                errorDiv.html(`
                                    <span class="icon" role="alert">
                                        <i class="fas fa-times"></i>
                                    </span>
                                    <span>Order processing failed: ${xhr.responseText || 'Unknown error'}</span>
                                `);
                                card.update({ 'disabled': false });
                                submitButton.attr('disabled', false);
                            }
                        });
                    }
                });
            },
            error: function (xhr) {
                // Handle cache checkout data errors
                var errorDiv = $('#card-errors');
                errorDiv.html(`
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>Checkout validation failed: ${xhr.responseText || 'Unknown error'}</span>
                `);
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                submitButton.attr('disabled', false);
            }
        });
    });
});