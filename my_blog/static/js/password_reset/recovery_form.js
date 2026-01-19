document.addEventListener('DOMContentLoaded', function () {
    var inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(function (input) {
        input.classList.add('form-control');
    });
});
