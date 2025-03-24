/* jshint esversion: 6 */

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
        toggleBtn.setAttribute("aria-expanded", sidebar.classList.contains(
            "collapsed") ? "false" : "true"
        );
    });
});

const form = document.getElementById('username-form');

if (form) {
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        if (confirm('Are you sure you want to update your username?')) {
            const formData = new FormData(this);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('An error occurred: ' + error.message);
            });
        }
    });
}

function getCSRFToken() {
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (!token) {
        console.error('CSRF token not found');
        return '';
    }
    return token.value;
}

document.addEventListener('DOMContentLoaded', function () {
    const successAlerts = document.querySelectorAll('.alert-success');
    successAlerts.forEach(alert => {
        alert.classList.add('show');
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 150);
        }, 3000);
    });
});