if (isLoggedIn()) {
    redirectTo('/profile.html');
}

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        showAlert('两次密码输入不一致');
        return;
    }

    const userData = {
        username: document.getElementById('username').value,
        password: password,
        nickname: document.getElementById('nickname').value,
        email: document.getElementById('email').value || null,
        phone: document.getElementById('phone').value || null
    };

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('注册成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});
