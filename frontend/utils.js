function showAlert(message, type = 'error') {
    const alertDiv = document.getElementById('alert');
    if (alertDiv) {
        alertDiv.textContent = message;
        alertDiv.className = `alert alert-${type}`;
        alertDiv.classList.remove('hidden');
        setTimeout(() => {
            alertDiv.classList.add('hidden');
        }, 5000);
    }
}

function getHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
}

function handleResponse(response) {
    if (!response.ok) {
        return response.json().then(data => {
            throw new Error(data.detail || data.message || '请求失败');
        });
    }
    return response.json();
}

function saveToken(token) {
    localStorage.setItem('access_token', token);
}

function clearToken() {
    localStorage.removeItem('access_token');
}

function isLoggedIn() {
    return !!localStorage.getItem('access_token');
}

function redirectTo(path) {
    window.location.href = path;
}
