document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("toggle-btn");

    toggleBtn.addEventListener("click", function () {
        sidebar.classList.toggle("collapsed");
        toggleBtn.querySelector("i").classList.toggle("fa-arrow-left");
        toggleBtn.querySelector("i").classList.toggle("fa-arrow-right");
        toggleBtn.setAttribute("aria-expanded", sidebar.classList.contains("collapsed") ? "false" : "true");
    });
});