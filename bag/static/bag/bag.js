document.addEventListener("DOMContentLoaded", function () {
    const bagTable = document.querySelector("table");

    // Event Delegation for Update and Remove buttons
    bagTable.addEventListener("click", function (e) {
        if (e.target.classList.contains("update-link")) {
            e.preventDefault();
            const row = e.target.closest("tr");
            const itemId = row.dataset.itemId;
            const quantityInput = row.querySelector(".quantity-input");
            let quantity = parseInt(quantityInput.value);

            if (!validateQuantity(quantity, quantityInput)) return;

            updateBag(itemId, quantity, row);
        }

        if (e.target.classList.contains("remove-item")) {
            e.preventDefault();
            const itemId = e.target.dataset.itemId;
            removeFromBag(itemId, e.target);
        }
    });

    // Prevent users from manually entering invalid quantities
    document.querySelectorAll(".quantity-input").forEach(input => {
        input.addEventListener("input", function () {
            let quantity = parseInt(this.value);

            if (isNaN(quantity) || quantity < 1) {
                this.value = 1; // Reset to 1 if invalid
            } else if (quantity > 10) {
                alert("Maximum quantity allowed is 10.");
                this.value = 10;
            }
        });
    });

    function validateQuantity(quantity, inputField) {
        if (isNaN(quantity) || quantity < 1) {
            alert("Quantity must be at least 1.");
            inputField.value = 1;
            return false;
        } else if (quantity > 10) {
            alert("Maximum quantity allowed is 10.");
            inputField.value = 10;
            return false;
        }
        return true;
    }

    function updateBag(itemId, quantity, row) {
        fetch(`/bag/update/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ 'quantity': quantity }),
        })
        .then(response => response.json())
        .then(response => {
            if (response.success) {
                row.querySelector(".line-total").textContent = `£${response.subtotal.toFixed(2)}`;
                document.getElementById("total").textContent = response.grand_total.toFixed(2);

                const bagCounter = document.querySelector('.bag-counter');
                if (bagCounter) {
                    bagCounter.textContent = response.item_count;
                }

                showToast('success', response.message);
            } else {
                showToast('error', response.error || "Error updating bag.");
            }
        })
        .catch(error => {
            console.error("Update error:", error);
            showToast('error', "Error updating bag.");
        });
    }

    function removeFromBag(itemId, button) {
        fetch(`/bag/remove/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({}),
        })
        .then(response => response.json())
        .then(response => {
            if (response.success) {
                const row = button.closest('tr');
                row.remove();
                document.getElementById("total").textContent = response.grand_total.toFixed(2);

                const bagCounter = document.querySelector('.bag-counter');
                if (bagCounter) {
                    bagCounter.textContent = response.item_count;
                }

                showToast('success', response.message);
            } else {
                showToast('error', response.error || "Error removing item.");
            }
        })
        .catch(error => {
            console.error("Remove error:", error);
            showToast('error', "Error removing item.");
        });
    }

    function getCSRFToken() {
        return document.getElementById("csrf_token") ? document.getElementById("csrf_token").value : "";
    }

    function showToast(type, message) {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
});
