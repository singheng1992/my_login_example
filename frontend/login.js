if (isLoggedIn()) {
    redirectTo('/profile.html');
}

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        this.classList.add('active');
        const tabName = this.dataset.tab;
        document.getElementById(`${tabName}-content`).classList.add('active');
    });
});

document.getElementById('password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('password-username').value;
    const password = document.getElementById('password-password').value;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/login/password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('登录成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

document.getElementById('send-email-btn').addEventListener('click', async function() {
    const email = document.getElementById('email-email').value;
    if (!email) {
        showAlert('请输入邮箱');
        return;
    }

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/send-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier: email })
        });
        const data = await handleResponse(response);
        showAlert(data.message || '验证码已发送', 'success');

        let countdown = 60;
        this.disabled = true;
        const timer = setInterval(() => {
            this.textContent = `${countdown}s`;
            countdown--;
            if (countdown < 0) {
                clearInterval(timer);
                this.disabled = false;
                this.textContent = '发送验证码';
            }
        }, 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

document.getElementById('email-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email-email').value;
    const code = document.getElementById('email-code').value;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/login/email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('登录成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

document.getElementById('send-sms-btn').addEventListener('click', async function() {
    const phone = document.getElementById('sms-phone').value;
    if (!phone) {
        showAlert('请输入手机号');
        return;
    }

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/send-sms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier: phone })
        });
        const data = await handleResponse(response);
        showAlert(data.message || '验证码已发送', 'success');

        let countdown = 60;
        this.disabled = true;
        const timer = setInterval(() => {
            this.textContent = `${countdown}s`;
            countdown--;
            if (countdown < 0) {
                clearInterval(timer);
                this.disabled = false;
                this.textContent = '发送验证码';
            }
        }, 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

document.getElementById('sms-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const phone = document.getElementById('sms-phone').value;
    const code = document.getElementById('sms-code').value;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/login/sms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code })
        });
        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('登录成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

document.querySelectorAll('.oauth-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const provider = this.dataset.provider;
        const authUrl = config.oauthProviders[provider];
        if (authUrl) {
            window.location.href = authUrl;
        } else {
            showAlert('该登录方式暂未配置');
        }
    });
});
