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
    const card = elements.create("card", {
        style: style,
        hidePostalCode: true
    });
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
        card.update({ 'disabled': true });

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
        console.log("Payment result:", result); // Debug the response
        const cardErrors = document.getElementById("card-errors");
        const successMessage = document.getElementById("payment-success");

        if (result.error) {
            cardErrors.textContent = result.error.message;
            cardErrors.style.display = "block";
            submitButton.disabled = false;
            card.update({ 'disabled': false });
        } else if (result.paymentIntent.status === "succeeded") {
            successMessage.textContent = "Payment successful! Redirecting...";
            successMessage.style.display = "block";
            console.log("Success block reached"); // Confirm this runs
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } else {
            console.log("Unexpected paymentIntent status:", result.paymentIntent.status);
        }
    }

    // Handle form submission
    function sendOrderDetails() {
        fetch('/checkout/save-order/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({
                full_name: form.full_name.value,
                email: form.email.value,
                phone_number: form.phone_number.value,
                address: {
                    street_address1: form.street_address1.value,
                    street_address2: form.street_address2.value,
                    town_or_city: form.town_or_city.value,
                    county: form.county.value,
                    postcode: form.postcode.value,
                    country: form.country.value
                }
            })
        }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message and reload the page after 3 seconds
                    document.getElementById("payment-success").textContent = "Payment successful! Reloading...";
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                } else {
                    document.getElementById("card-errors").textContent = "Error processing payment.";
                    submitButton.disabled = false;
                    card.update({ 'disabled': false });
                }
            })
            .catch(error => {
                console.error("Error:", error);
                document.getElementById("card-errors").textContent = "Error processing payment.";
                submitButton.disabled = false;
                card.update({ 'disabled': false });
            });
    }
});
