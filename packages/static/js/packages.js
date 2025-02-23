document.addEventListener("DOMContentLoaded", function () {
    const quantityInput = document.getElementById("quantity");
    const quantityError = document.getElementById("quantity-error");

    quantityInput.addEventListener("input", function () {
        let quantity = parseInt(this.value);

        if (isNaN(quantity) || quantity < 1) {
            this.value = 1;
        } else if (quantity > 10) {
            this.value = 10;
            quantityError.style.display = "block";
        } else {
            quantityError.style.display = "none"; 
        }
    });
});