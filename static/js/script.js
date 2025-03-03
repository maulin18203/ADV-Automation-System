//SCRIPT.JS
console.log("IoT Home Automation Site");

// Fetch data from a RESTful API
function fetchData(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
}

// WebSocket setup
const socket = new WebSocket('ws://localhost:5000/ws');
socket.onopen = () => console.log('WebSocket is open');
socket.onmessage = event => console.log('Received:', event.data);
socket.onerror = error => console.error('WebSocket Error:', error);
socket.onclose = () => console.log('WebSocket is closed');

// Fetch data with authentication (Bearer Token)
function fetchWithAuth(url) {
    fetch(url, {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        }
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

// Login and logout
function login() {
    fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'password' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.token);
            window.location.href = '/';
        } else {
            alert('Invalid credentials');
        }
    });
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

// Toggle functions for UI elements
function toggleClass(elementId) {
    const element = document.getElementById(elementId);
    if (element) element.classList.toggle('active');
}

// Example: Toggle Sidebar
function toggleSidebar() {
    toggleClass('sidebar');
    toggleClass('content');
}

// Show search suggestions
function showSuggestions(value) {
    const suggestions = document.getElementById('suggestions');
    suggestions.innerHTML = '';
    if (value.length > 0) {
        fetch('/api/users/search?query=' + value)
            .then(response => response.json())
            .then(data => {
                data.forEach(user => {
                    const suggestion = document.createElement('div');
                    suggestion.classList.add('suggestion');
                    suggestion.textContent = user.name;
                    suggestions.appendChild(suggestion);
                });
            })
            .catch(error => console.error('Error:', error));
    }
}
