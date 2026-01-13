if (!isLoggedIn()) {
    redirectTo('/login.html');
}

async function loadProfile() {
    try {
        const response = await fetch(`${config.apiBaseUrl}/api/user/profile`, {
            headers: getHeaders()
        });
        const data = await handleResponse(response);
        const user = data.data;

        document.getElementById('username').textContent = user.username || '-';
        document.getElementById('nickname').textContent = user.nickname;
        document.getElementById('email').textContent = user.email || '-';
        document.getElementById('phone').textContent = user.phone || '-';

        if (user.avatar_url) {
            document.getElementById('avatar-img').src = user.avatar_url.startsWith('http')
                ? user.avatar_url
                : `${config.apiBaseUrl}${user.avatar_url}`;
        }
    } catch (error) {
        showAlert(error.message);
        if (error.message.includes('401')) {
            clearToken();
            redirectTo('/login.html');
        }
    }
}

document.getElementById('update-btn').addEventListener('click', async () => {
    const nickname = document.getElementById('new-nickname').value;
    if (!nickname) {
        showAlert('请输入新昵称');
        return;
    }

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/user/profile`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify({ nickname })
        });
        const data = await handleResponse(response);
        showAlert(data.message || '更新成功', 'success');
        document.getElementById('new-nickname').value = '';
        loadProfile();
    } catch (error) {
        showAlert(error.message);
    }
});

document.getElementById('avatar-file').addEventListener('change', async function() {
    const file = this.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/user/avatar`, {
            method: 'POST',
            headers: {
                ...(localStorage.getItem('access_token') && { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` })
            },
            body: formData
        });
        const data = await handleResponse(response);
        showAlert(data.message || '头像上传成功', 'success');
        loadProfile();
    } catch (error) {
        showAlert(error.message);
    }
});

document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch(`${config.apiBaseUrl}/api/auth/logout`, {
            method: 'POST',
            headers: getHeaders()
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    clearToken();
    showAlert('已退出登录', 'success');
    setTimeout(() => redirectTo('/login.html'), 1000);
});

loadProfile();
