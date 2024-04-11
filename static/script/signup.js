const passwordInput = document.getElementById('password');

    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$/;

        if (!passwordRegex.test(password)) {
            this.setCustomValidity("Password must contain at least one capital letter, one small letter, one symbol, and be a minimum of 8 characters long");
        } else {
            this.setCustomValidity('');
        }
    });