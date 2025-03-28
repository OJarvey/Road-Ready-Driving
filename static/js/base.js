/* jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function() {
    const mobileSearchButton = document.getElementById('mobileSearchButton');
    const mobileSearchForm = document.getElementById('mobileSearchForm');

    mobileSearchButton.addEventListener('click', function(event) {
        event.stopPropagation();
        if (mobileSearchForm.style.display === 'none' || mobileSearchForm.style.display === '') {
            mobileSearchForm.style.display = 'block';
        } else {
            mobileSearchForm.style.display = 'none';
        }
    });

    const navbarToggler = document.querySelector('.navbar-toggler');
    navbarToggler.addEventListener('click', function() {
        mobileSearchForm.style.display = 'none';
    });

    document.addEventListener('click', function(event) {
        const isClickInsideForm = mobileSearchForm.contains(event.target);
        const isClickOnButton = mobileSearchButton.contains(event.target);

        if (!isClickInsideForm && !isClickOnButton && mobileSearchForm.style.display === 'block') {
            mobileSearchForm.style.display = 'none';
        }
    });
});