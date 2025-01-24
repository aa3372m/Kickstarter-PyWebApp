// Theme Management
function setTheme(themeName) {
    const themeLink = document.getElementById('theme-css');
    const newHref = `/static/css/themes/${themeName}.css`;
    
    // Create a new link element
    const newLink = document.createElement('link');
    newLink.rel = 'stylesheet';
    newLink.id = 'theme-css';
    newLink.href = newHref;
    
    // Add the new link and remove the old one after it loads
    newLink.onload = () => {
        if (themeLink) {
            themeLink.remove();
        }
    };
    
    document.head.appendChild(newLink);
    
    // Store theme preference
    localStorage.setItem('theme', themeName);
}

// Flash Messages
function createFlashMessage(message, category = 'info', timeout = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${category} alert-dismissible alert-floating fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, timeout);
}

// Form Validation
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Password Strength Meter
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;
    
    return strength;
}

// Loading Spinner
function showSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    document.body.appendChild(spinner);
}

function hideSpinner() {
    const spinner = document.querySelector('.spinner');
    if (spinner) {
        spinner.remove();
    }
}

// AJAX Request Helper
async function fetchAPI(url, options = {}) {
    try {
        showSpinner();
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        createFlashMessage(error.message, 'error');
        throw error;
    } finally {
        hideSpinner();
    }
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize Bootstrap Tooltips and Popovers
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            if (!validateForm(form)) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });
}); 