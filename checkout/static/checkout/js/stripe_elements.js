document.addEventListener("DOMContentLoaded", function () {

    //Get Stripe Public Key & Client Secret

    const stripePublicKey = document.getElementById("stripe-public-key")?.textContent;
    const clientSecret = document.getElementById("client-secret")?.textContent;

    if (!stripePublicKey || !clientSecret) {
        console.error(" Stripe Public Key or Client Secret is missing.");
        return;
    }


    //Initialize Stripe Elements

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    const style = {
        base: {
            color: "#000",
            fontFamily: '"Roboto", sans-serif',
            fontSmoothing: "antialiased",
            fontSize: "16px",
            "::placeholder": { color: "#aab7c4" }
        },
        invalid: {
            color: "#dc3545",
            iconColor: "#dc3545"
        }
    };

    // Mount Stripe Card Element
    const card = elements.create("card", { style });
    card.mount("#card-element");


    //Handle Real-time Card Validation Errors

    card.addEventListener("change", function (event) {
        const displayError = document.getElementById("card-errors");
        displayError.textContent = event.error ? event.error.message : "";
    });

    //Handle Form Submission

    const form = document.getElementById("payment-form");
    const submitButton = document.getElementById("submit-button");

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        submitButton.disabled = true;

        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: getBillingDetails(form),
            }
        }).then(handlePaymentResult);
    });


    // Extract billing details from form
    function getBillingDetails(form) {
        return {
            name: form.full_name.value,
            email: form.email.value,
            phone: form.phone_number.value,
            address: {
                line1: form.street_address1.value,
                line2: form.street_address2.value,
                city: form.town_or_city.value,
                country: form.country.value,
                postal_code: form.postcode.value
            }
        };
    }

    // Handle payment result
    function handlePaymentResult(result) {
        if (result.error) {
            document.getElementById("card-errors").textContent = result.error.message;
            submitButton.disabled = false;
        } else if (result.paymentIntent.status === "succeeded") {
            form.submit();
        }
    }
});
