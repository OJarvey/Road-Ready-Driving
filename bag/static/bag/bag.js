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
                showToast('warning', "⚠ Maximum quantity allowed is 10.");
                this.value = 10;
            }
        });
    });

    function validateQuantity(quantity, inputField) {
        if (!inputField.value) {
            showToast('warning', "⚠ Please enter a valid quantity.");
            inputField.value = 1;
            return false;
        }
        if (isNaN(quantity) || quantity < 1) {
            showToast('warning', "⚠ Quantity must be at least 1.");
            inputField.value = 1;
            return false;
        } else if (quantity > 10) {
            showToast('warning', "⚠ Maximum quantity allowed is 10.");
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
                row.querySelector(".line-total").textContent = `${response.subtotal.toFixed(2)}`;
                document.getElementById("total").textContent = response.grand_total.toFixed(2);

                document.querySelectorAll('.shopping-bag .badge').forEach(el => {
                    el.textContent = response.item_count;
                    el.style.display = response.item_count > 0 ? 'block' : 'none';
                });

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
                window.updateBagBadge(response.item_count);
                if (response.item_count === 0) {
                    const container = document.querySelector('.container .row .col-12');
                    container.innerHTML = `
                        <div class="text-center my-5">
                            <p class="lead">Your bookings are currently empty.</p>
                            <a href="/packages/packages/" class="btn btn-outline-primary btn-lg">
                                <i class="fas fa-chevron-left"></i> Book a Driving Package
                            </a>
                        </div>
                    `;
                }
                window.showToast('success', response.message);
            } else {
                window.showToast('error', response.error || "Error removing item.");
            }
        })
        .catch(error => {
            console.error("Remove error:", error);
            window.showToast('error', "Error removing item.");
        });
    }

    function getCSRFToken() {
        const token = document.getElementById("csrf_token");
        return token ? token.value : document.querySelector("[name=csrfmiddlewaretoken]").value;
    }

    function showToast(type, message) {
        const toastContainer = document.querySelector('.message-container') || document.createElement('div');
        if (!toastContainer.classList.contains('message-container')) {
            toastContainer.classList.add('message-container');
            document.body.appendChild(toastContainer);
        }

        const toastHTML = `
            <div class="toast custom-toast rounded-0 border-top-0" data-bs-autohide="false">
                <div class="arrow-up arrow-${type}"></div>
                <div class="w-100 toast-capper bg-${type}"></div>
                <div class="toast-header bg-white text-dark">
                    <strong class="mr-auto">${type.charAt(0).toUpperCase() + type.slice(1)}!</strong>
                    <button type="button" class="ml-2 mb-1 close text-dark" data-bs-dismiss="toast" aria-label="Close">
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
                <div class="toast-body bg-white">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.innerHTML += toastHTML;
        const toastEl = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastEl, { autohide: false });
        toast.show();

        // Optional: Auto-hide after 4 seconds but allow manual dismissal
        setTimeout(() => {
            toast.hide(); // Hide with animation
            setTimeout(() => toastEl.remove(), 300); // Remove after animation
        }, 4000);
    }
});