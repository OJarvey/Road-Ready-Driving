document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("toggle-btn");

    if (window.innerWidth <= 768) {
        sidebar.classList.add("collapsed");
        toggleBtn.setAttribute("aria-expanded", "false");
    }

    toggleBtn.addEventListener("click", function () {
        sidebar.classList.toggle("collapsed");
        toggleBtn.querySelector("i").classList.toggle("fa-arrow-left");
        toggleBtn.querySelector("i").classList.toggle("fa-arrow-right");
        toggleBtn.setAttribute("aria-expanded", sidebar.classList.contains("collapsed") ? "false" : "true");
    });
});

document.getElementById('username-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Show confirmation dialog
    if (confirm('Are you sure you want to update your username?')) {
        // If confirmed, submit the form via fetch
        const form = this;
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // For Django to recognize AJAX
            }
        })
        .then(response => {
            if (response.ok) {
                // Show success message
                const successMsg = document.getElementById('success-message');
                successMsg.style.display = 'block';
                // Hide after 3 seconds
                setTimeout(() => {
                    successMsg.style.display = 'none';
                }, 3000);
                // Reset form or update UI
                form.querySelector('input[name="username"]').value = formData.get('username');
            } else {
                alert('Error updating username. Please try again.');
            }
        })
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const successAlerts = document.querySelectorAll('.alert-success');
    successAlerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 150); // Remove from DOM after fade
        }, 3000);
    });
});