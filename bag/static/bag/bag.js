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

            if (isNaN(quantity) || quantity < 1) {
                alert("Quantity must be at least 1.");
                quantityInput.value = 1;
                return;
            }

            updateBag(itemId, quantity, row);
        }

        if (e.target.classList.contains("remove-item")) {
            e.preventDefault();
            const itemId = e.target.dataset.itemId;
            removeFromBag(itemId, e.target);
        }
    });

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
        return document.getElementById("csrf_token").value;
    }

    function showToast(type, message) {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
});
