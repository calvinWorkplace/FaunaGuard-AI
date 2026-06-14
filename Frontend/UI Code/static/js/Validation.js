const form = document.getElementById('form');
const Username_input = document.getElementById('Username_input');
const Password_input = document.getElementById('Password_input');
const email_input = document.getElementById('email_input');
const error_message = document.getElementById('error_message');

form.addEventListener('submit', (e) => {
    let errors = [];

    if (email_input) {
        // Signup form
        errors = getSignupFormErrors(Username_input.value, Password_input.value, email_input.value);
    } else {
        // Login form
        errors = getLoginFormErrors(Username_input.value, Password_input.value);
    }

    if (errors.length > 0) {
        e.preventDefault();
        error_message.innerText = errors.join(". ");
    }
});

function getSignupFormErrors(Username, Password, email) {
    let errors = [];

    if (Username === '' || Username == null) {
        errors.push('Username is required');
        Username_input.parentElement.classList.add('incorrect');
    }
    if (email === '' || email == null) {
        errors.push('Email is required');
        email_input.parentElement.classList.add('incorrect');
    }
    if (Password === '' || Password == null) {
        errors.push('Password is required');
        Password_input.parentElement.classList.add('incorrect');
    } else if (Password.length < 6) {
        errors.push('Password must have at least 6 characters');
        Password_input.parentElement.classList.add('incorrect');
    }

    return errors;
}

function getLoginFormErrors(Username, Password) {
    let errors = [];

    if (Username === '' || Username == null) {
        errors.push('Username is required');
        Username_input.parentElement.classList.add('incorrect');
    }
    if (Password === '' || Password == null) {
        errors.push('Password is required');
        Password_input.parentElement.classList.add('incorrect');
    } else if (Password.length < 6) {
        errors.push('Password must have at least 6 characters');
        Password_input.parentElement.classList.add('incorrect');
    }

    return errors;
}

const allInputs = [Username_input, Password_input, email_input].filter(input => input != null);

allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if (input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect');
            error_message.innerText = '';
        }
    });
});

function previewImage(input) {
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewContainer.style.display = 'block';
        };

        reader.readAsDataURL(input.files[0]);
    } else {
        previewContainer.style.display = 'none';
        previewImage.src = "";
    }
}
