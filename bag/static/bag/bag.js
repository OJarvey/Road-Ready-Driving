/* jshint esversion: 6 */
/* global packagesUrl */
/* global packagesUrl, bootstrap */

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
        if (!card || !card.querySelector) {
            console.error('Invalid card element');
            return;
        }
        fetch(`/bag/update/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ 'quantity': quantity }),
        })
        .then(response => {
            if (!response.ok) throw new Error('Server error: ' + response.status);
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const lineTotal = card.querySelector(".line-total");
                if (lineTotal) lineTotal.textContent = `£${data.subtotal.toFixed(2)}`;
    
                document.querySelectorAll("#total, #total-mobile").forEach(el => {
                    el.textContent = `£${data.grand_total.toFixed(2)}`;
                });
    
                document.querySelectorAll(".shopping-bag .badge").forEach(el => {
                    el.textContent = data.item_count;
                    el.style.display = data.item_count > 0 ? 'block' : 'none';
                });
    
                showToast('success', data.message, 'Item updated successfully');
            } else {
                showToast('error', data.error, 'Failed to update item');
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
                    ".shopping-bag .badge").forEach(el => {
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
        setTimeout(() => {
            toast.hide();
            setTimeout(() => toastEl.remove(), 300);
        }, 4000);
    }
});