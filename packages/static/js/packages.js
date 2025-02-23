document.addEventListener("DOMContentLoaded", function () {
    const quantityInput = document.getElementById("quantity");
    const quantityError = document.getElementById("quantity-error");
    const form = quantityInput.closest('form');
    const submitButton = form.querySelector('button[type="submit"]');

    // Validate quantity input on change
    quantityInput.addEventListener("input", function () {
        let quantity = parseInt(this.value);

        if (isNaN(quantity) || quantity < 1) {
            this.value = 1;
            quantityError.textContent = "Quantity must be at least 1.";
            quantityError.style.display = "block";
        } else if (quantity > 10) {
            this.value = 10;
            quantityError.textContent = "Maximum quantity is 10.";
            quantityError.style.display = "block";
        } else {
            quantityError.style.display = "none";
        }
    });

    // Handle form submission via AJAX
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        let quantity = parseInt(quantityInput.value);

        if (quantity > 10) {
            quantityError.textContent = "Cannot add more than 10 items.";
            quantityError.style.display = "block";
            return;
        }

        submitButton.disabled = true;

        fetch(form.action, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest"
            },
            body: new URLSearchParams(new FormData(form)),
        })
        .then(response => response.json())
        .then(data => {
            submitButton.disabled = false;
            if (data.success) {
                quantityError.style.display = "none";
                showToast('success', data.message);
                const bagBadge = document.querySelector('.shopping-bag .badge');
                if (bagBadge) {
                    bagBadge.textContent = data.item_count;
                    bagBadge.style.display = data.item_count > 0 ? 'block' : 'none';
                }
            } else {
                quantityError.textContent = data.error;
                quantityError.style.display = "block";
                showToast('error', data.error);
            }
        })
        .catch(error => {
            submitButton.disabled = false;
            quantityError.textContent = "Error adding to bag.";
            quantityError.style.display = "block";
            showToast('error', "Error adding to bag.");
        });
    });

    // Toast notification function (consistent with bag.js)
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