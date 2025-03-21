document.addEventListener("DOMContentLoaded", function () {
    const bagContainer = document.querySelector(".col-12.col-lg-8");

    // Event Delegation for Update and Remove buttons
    bagContainer.addEventListener("click", function (e) {
        // Update Quantity
        if (e.target.classList.contains("update-link")) {
            e.preventDefault();
            const card = e.target.closest(".mobile-booking-card, tr");
            if (!card) return;
            const quantityInput = card.querySelector(".quantity-input");
            if (!quantityInput) return;
            const itemId = quantityInput.dataset.itemId;
            const quantity = parseInt(quantityInput.value);

            if (!validateQuantity(quantity, quantityInput)) return;

            updateBag(itemId, quantity, card);
        }

        // Remove Item
        if (e.target.classList.contains("remove-item")) {
            e.preventDefault();
            const itemId = e.target.dataset.itemId;
            const card = e.target.closest(".mobile-booking-card, tr");
            removeFromBag(itemId, card);
        }
    });

    // Quantity input validation
    document.querySelectorAll(".quantity-input").forEach(input => {
        input.addEventListener("input", function () {
            let quantity = parseInt(this.value) || 1;
            this.value = Math.min(Math.max(quantity, 1), 10);
        });
    });

    function validateQuantity(quantity, inputField) {
        if (isNaN(quantity) || quantity < 1 || quantity > 10) {
            inputField.value = 1;
            showToast('warning', "Please enter a quantity between 1 and 10.");
            return false;
        }
        return true;
    }

    function updateBag(itemId, quantity, card) {
        fetch(`/bag/update/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ 'quantity': quantity }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update line total
                card.querySelector(
                    ".line-total").textContent = `£${data.subtotal.toFixed(2)}`;
                // Update grand total
                document.querySelectorAll(
                    "#total, #total-mobile").forEach(el => {
                    el.textContent = `£${data.grand_total.toFixed(2)}`;
                });
                // Update item count
                document.querySelectorAll(
                    ".bag-counter, .bag-counter-mobile").forEach(el => {
                    el.textContent = data.item_count;
                });
                showToast('success', data.message);
            } else {
                showToast('error', data.error);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showToast('error', "An error occurred while updating.");
        });
    }

    function removeFromBag(itemId, card) {
        fetch(`/bag/remove/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove item from UI
                card.remove();
                // Update totals
                document.querySelectorAll(
                    "#total, #total-mobile").forEach(el => {
                    el.textContent = `£${data.grand_total.toFixed(2)}`;
                });
                // Update item count
                document.querySelectorAll(
                    ".bag-counter, .bag-counter-mobile").forEach(el => {
                    el.textContent = data.item_count;
                });
                // Show empty state if needed
                if (data.item_count === 0) {
                    bagContainer.innerHTML = `
                        <div class="text-center my-5">
                            <p class="lead">
                            Your bookings are currently empty.</p>
                            <a href="
                            ${packagesUrl}" class="btn btn-outline-secondary"
                            >
                                <i class="
                                fas fa-chevron-left"></i> Book a Driving Package
                            </a>
                        </div>
                    `;
                }
                showToast('success', data.message);
            } else {
                showToast('error', data.error);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showToast('error', "An error occurred while removing.");
        });
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showToast(type, message) {
        $('.toast').toast('show');
    }
});