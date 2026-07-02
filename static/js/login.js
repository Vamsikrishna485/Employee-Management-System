document.addEventListener("DOMContentLoaded", function () {

    const password = document.querySelector("#password");
    const eye = document.querySelector("#togglePassword");

    eye.onclick = function () {

        if (password.getAttribute("type") === "password") {

            password.setAttribute("type", "text");

            eye.classList.remove("fa-eye");
            eye.classList.add("fa-eye-slash");

        } else {

            password.setAttribute("type", "password");

            eye.classList.remove("fa-eye-slash");
            eye.classList.add("fa-eye");

        }

    };

});