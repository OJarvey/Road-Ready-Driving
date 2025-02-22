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

            if (!this.value) {
                this.value = 1;
            } else if (isNaN(quantity) || quantity < 1) {
                this.value = 1;
            } else if (quantity > 10) {
                alert("⚠ Maximum quantity allowed is 10.");
                this.value = 10;
            }
        });
    });

    function validateQuantity(quantity, inputField) {
        if (!inputField.value) {
            alert("⚠ Please enter a valid quantity.");
            inputField.value = 1;
            return false;
        }
        if (isNaN(quantity) || quantity < 1) {
            alert("⚠ Quantity must be at least 1.");
            inputField.value = 1;
            return false;
        } else if (quantity > 10) {
            alert("⚠ Maximum quantity allowed is 10.");
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
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(response => {
                if (response.success) {
                    // Convert to numbers explicitly
                    const subtotal = Number(response.subtotal);
                    const grandTotal = Number(response.grand_total);

                    // Update totals with fixed decimal places
                    // Change this line in the updateBag function
                    row.querySelector(".line-total").textContent =
                        response.subtotal.toFixed(2);
                    document.getElementById("total").textContent =
                        grandTotal.toFixed(2);

                    // Update bag counter
                    document.querySelectorAll('.bag-counter').forEach(el => {
                        el.textContent = response.item_count;
                    });
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Update failed: " + error.message);
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
                    // Remove the row instantly
                    const row = button.closest('tr');
                    row.remove();

                    // Update grand total in real-time
                    document.getElementById("total").textContent = response.grand_total.toFixed(2);

                    // Update bag counter
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
        const token = document.getElementById("csrf_token");
        return token ? token.value : document.querySelector("[name=csrfmiddlewaretoken]").value;
    }

    function showToast(type, message) {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
});
