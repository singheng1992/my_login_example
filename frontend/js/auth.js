/**
 * 认证模块 - 登录注册逻辑
 */

// ==================== 密码登录 ====================

/**
 * 密码登录
 */
async function loginWithPassword() {
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const loginBtn = document.getElementById('btn-login-password');

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    // 验证
    let isValid = true;

    if (!username) {
        showFieldError(usernameInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('username', username)) {
        showFieldError(usernameInput, errorMessages.username);
        isValid = false;
    }

    if (!password) {
        showFieldError(passwordInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('password', password)) {
        showFieldError(passwordInput, errorMessages.password);
        isValid = false;
    }

    if (!isValid) return;

    // 禁用表单
    loginBtn.disabled = true;
    loginBtn.textContent = '登录中...';

    try {
        const response = await post(API_ENDPOINTS.LOGIN_PASSWORD, {
            username,
            password
        });

        // 保存token和用户信息
        saveToken(response.data.access_token);
        saveUserInfo(response.data.user);

        toast.success('登录成功');

        // 延迟切换视图
        setTimeout(() => {
            switchView('user-view');
            loadUserProfile();
        }, 500);

    } catch (error) {
        toast.error(error.message || '登录失败');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = '登录';
    }
}

// ==================== 邮箱验证码登录 ====================

/**
 * 发送邮箱验证码
 */
async function sendEmailCode() {
    const emailInput = document.getElementById('login-email');
    const email = emailInput.value.trim();

    // 验证邮箱格式
    if (!email) {
        showFieldError(emailInput, errorMessages.required);
        return;
    }

    if (!validateField('email', email)) {
        showFieldError(emailInput, errorMessages.email);
        return;
    }

    const sendBtn = document.getElementById('btn-send-email');
    sendBtn.disabled = true;
    sendBtn.textContent = '发送中...';

    try {
        await post(API_ENDPOINTS.SEND_EMAIL, { identifier: email });
        toast.success('验证码已发送到您的邮箱');

        // 开始倒计时
        countdown.start('btn-send-email');

    } catch (error) {
        toast.error(error.message || '发送失败');
        sendBtn.disabled = false;
        sendBtn.textContent = '发送验证码';
    }
}

/**
 * 邮箱验证码登录
 */
async function loginWithEmail() {
    const emailInput = document.getElementById('login-email');
    const codeInput = document.getElementById('login-email-code');
    const loginBtn = document.getElementById('btn-login-email');

    const email = emailInput.value.trim();
    const code = codeInput.value.trim();

    // 验证
    let isValid = true;

    if (!email) {
        showFieldError(emailInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('email', email)) {
        showFieldError(emailInput, errorMessages.email);
        isValid = false;
    }

    if (!code) {
        showFieldError(codeInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('code', code)) {
        showFieldError(codeInput, errorMessages.code);
        isValid = false;
    }

    if (!isValid) return;

    // 禁用表单
    loginBtn.disabled = true;
    loginBtn.textContent = '登录中...';

    try {
        const response = await post(API_ENDPOINTS.LOGIN_EMAIL, {
            email,
            code
        });

        // 保存token和用户信息
        saveToken(response.data.access_token);
        saveUserInfo(response.data.user);

        toast.success('登录成功');

        // 延迟切换视图
        setTimeout(() => {
            switchView('user-view');
            loadUserProfile();
        }, 500);

    } catch (error) {
        toast.error(error.message || '登录失败');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = '登录';
    }
}

// ==================== 手机验证码登录 ====================

/**
 * 发送短信验证码
 */
async function sendSmsCode() {
    const phoneInput = document.getElementById('login-phone');
    const phone = phoneInput.value.trim();

    // 验证手机号格式
    if (!phone) {
        showFieldError(phoneInput, errorMessages.required);
        return;
    }

    if (!validateField('phone', phone)) {
        showFieldError(phoneInput, errorMessages.phone);
        return;
    }

    const sendBtn = document.getElementById('btn-send-sms');
    sendBtn.disabled = true;
    sendBtn.textContent = '发送中...';

    try {
        await post(API_ENDPOINTS.SEND_SMS, { identifier: phone });
        toast.success('验证码已发送到您的手机');

        // 开始倒计时
        countdown.start('btn-send-sms');

    } catch (error) {
        toast.error(error.message || '发送失败');
        sendBtn.disabled = false;
        sendBtn.textContent = '发送验证码';
    }
}

/**
 * 手机验证码登录
 */
async function loginWithPhone() {
    const phoneInput = document.getElementById('login-phone');
    const codeInput = document.getElementById('login-phone-code');
    const loginBtn = document.getElementById('btn-login-phone');

    const phone = phoneInput.value.trim();
    const code = codeInput.value.trim();

    // 验证
    let isValid = true;

    if (!phone) {
        showFieldError(phoneInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('phone', phone)) {
        showFieldError(phoneInput, errorMessages.phone);
        isValid = false;
    }

    if (!code) {
        showFieldError(codeInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('code', code)) {
        showFieldError(codeInput, errorMessages.code);
        isValid = false;
    }

    if (!isValid) return;

    // 禁用表单
    loginBtn.disabled = true;
    loginBtn.textContent = '登录中...';

    try {
        const response = await post(API_ENDPOINTS.LOGIN_SMS, {
            phone,
            code
        });

        // 保存token和用户信息
        saveToken(response.data.access_token);
        saveUserInfo(response.data.user);

        toast.success('登录成功');

        // 延迟切换视图
        setTimeout(() => {
            switchView('user-view');
            loadUserProfile();
        }, 500);

    } catch (error) {
        toast.error(error.message || '登录失败');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = '登录';
    }
}

// ==================== OAuth登录 ====================

/**
 * OAuth登录
 */
async function loginWithOAuth(provider) {
    try {
        // 保存当前URL，用于回调后返回
        sessionStorage.setItem('oauth_return_url', window.location.href);

        // 获取授权URL
        const response = await get(`${API_ENDPOINTS.OAUTH}/${provider}`);
        const authUrl = response.data.auth_url;

        // 直接跳转到OAuth授权页面（不要修改redirect_uri）
        window.location.href = authUrl;

    } catch (error) {
        toast.error(error.message || 'OAuth登录失败');
    }
}

/**
 * 处理OAuth回调
 * 后端处理完OAuth后会重定向回前端，并传递token参数
 */
function handleOAuthCallback() {
    // 从 URL fragment (hash) 中获取 token
    const hash = window.location.hash;
    const tokenMatch = hash.match(/token=([^&]+)/);

    // 从 URL query 中获取 error
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');

    if (error) {
        toast.error(decodeURIComponent(error));
        // 清除URL参数
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
    }

    if (tokenMatch) {
        const token = tokenMatch[1];

        // 保存token
        saveToken(token);

        // 获取用户信息
        loadUserProfile().then((userInfo) => {
            toast.success('登录成功');
            switchView('user-view');

            // 清除URL fragment
            window.history.replaceState({}, document.title, window.location.pathname);

            // 检查用户是否有邮箱，没有则弹出补全模态框
            if (!userInfo || !userInfo.email) {
                // 稍微延迟弹出，让用户先看到登录成功
                setTimeout(() => {
                    showEmailCompletionModal();
                }, 500);
            }
        }).catch(() => {
            // 如果获取用户信息失败，至少切换视图
            switchView('user-view');
            window.history.replaceState({}, document.title, window.location.pathname);
        });
    }
}

// ==================== 注册 ====================

/**
 * 注册账号
 */
async function register() {
    const usernameInput = document.getElementById('reg-username');
    const passwordInput = document.getElementById('reg-password');
    const confirmPasswordInput = document.getElementById('reg-confirm-password');
    const emailInput = document.getElementById('reg-email');
    const phoneInput = document.getElementById('reg-phone');
    const nicknameInput = document.getElementById('reg-nickname');
    const registerBtn = document.getElementById('btn-register');

    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const email = emailInput.value.trim() || undefined;
    const phone = phoneInput.value.trim() || undefined;
    const nickname = nicknameInput.value.trim();

    // 验证
    let isValid = true;

    // 用户名（必填）
    if (!username) {
        showFieldError(usernameInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('username', username)) {
        showFieldError(usernameInput, errorMessages.username);
        isValid = false;
    }

    // 密码（必填）
    if (!password) {
        showFieldError(passwordInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('password', password)) {
        showFieldError(passwordInput, errorMessages.password);
        isValid = false;
    }

    // 确认密码（必填）
    if (!confirmPassword) {
        showFieldError(confirmPasswordInput, errorMessages.required);
        isValid = false;
    } else if (password !== confirmPassword) {
        showFieldError(confirmPasswordInput, errorMessages.passwordMismatch);
        isValid = false;
    }

    // 邮箱（可选）
    if (email && !validateField('email', email)) {
        showFieldError(emailInput, errorMessages.email);
        isValid = false;
    }

    // 手机号（可选）
    if (phone && !validateField('phone', phone)) {
        showFieldError(phoneInput, errorMessages.phone);
        isValid = false;
    }

    // 昵称（必填）
    if (!nickname) {
        showFieldError(nicknameInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('nickname', nickname)) {
        showFieldError(nicknameInput, errorMessages.nickname);
        isValid = false;
    }

    if (!isValid) return;

    // 禁用表单
    registerBtn.disabled = true;
    registerBtn.textContent = '注册中...';

    try {
        const response = await post(API_ENDPOINTS.REGISTER, {
            username,
            password,
            email,
            phone,
            nickname
        });

        // 保存token和用户信息
        saveToken(response.data.access_token);
        saveUserInfo(response.data.user);

        toast.success('注册成功');

        // 延迟切换视图
        setTimeout(() => {
            switchView('user-view');
            loadUserProfile();
        }, 500);

    } catch (error) {
        toast.error(error.message || '注册失败');
    } finally {
        registerBtn.disabled = false;
        registerBtn.textContent = '注册';
    }
}

/**
 * 切换到注册表单
 */
function showRegisterForm() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');

    // 停止所有倒计时
    countdown.stopAll();
}

/**
 * 切换到登录表单
 */
function showLoginForm() {
    document.getElementById('register-form').classList.add('hidden');
    document.getElementById('login-form').classList.remove('hidden');

    // 停止所有倒计时
    countdown.stopAll();
}

// ==================== 退出登录 ====================

/**
 * 退出登录
 */
async function logout() {
    try {
        // 调用退出API
        await post(API_ENDPOINTS.LOGOUT, {});
    } catch (error) {
        // 忽略错误，继续清除本地状态
    } finally {
        // 清除本地存储
        removeToken();

        // 停止所有倒计时
        countdown.stopAll();

        // 切换到登录视图
        switchView('auth-view');

        // 清空表单
        document.querySelectorAll('input').forEach(input => {
            input.value = '';
        });

        toast.success('已退出登录');
    }
}

// ==================== 初始化 ====================

/**
 * 初始化认证模块
 */
function initAuthModule() {
    // 密码登录按钮
    document.getElementById('btn-login-password').addEventListener('click', loginWithPassword);

    // 发送邮箱验证码
    document.getElementById('btn-send-email').addEventListener('click', sendEmailCode);

    // 邮箱登录按钮
    document.getElementById('btn-login-email').addEventListener('click', loginWithEmail);

    // 发送短信验证码
    document.getElementById('btn-send-sms').addEventListener('click', sendSmsCode);

    // 手机登录按钮
    document.getElementById('btn-login-phone').addEventListener('click', loginWithPhone);

    // OAuth登录按钮
    document.querySelectorAll('.oauth-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const provider = btn.dataset.provider;
            loginWithOAuth(provider);
        });
    });

    // 注册按钮
    document.getElementById('btn-register').addEventListener('click', register);

    // 切换到注册表单
    document.getElementById('link-to-register').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
    });

    // 切换到登录表单
    document.getElementById('link-to-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });

    // 标签页切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab(btn.dataset.tab);
            countdown.stopAll();
        });
    });

    // 密码显示/隐藏切换
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                btn.textContent = '🙈';
            } else {
                input.type = 'password';
                btn.textContent = '👁️';
            }
        });
    });

    // 输入框验证 - 失去焦点时验证
    document.getElementById('login-username').addEventListener('blur', function() {
        if (this.value && !validateField('username', this.value.trim())) {
            showFieldError(this, errorMessages.username);
        }
    });

    document.getElementById('login-password').addEventListener('blur', function() {
        if (this.value && !validateField('password', this.value)) {
            showFieldError(this, errorMessages.password);
        }
    });

    document.getElementById('login-email').addEventListener('blur', function() {
        if (this.value && !validateField('email', this.value.trim())) {
            showFieldError(this, errorMessages.email);
        }
    });

    document.getElementById('login-phone').addEventListener('blur', function() {
        if (this.value && !validateField('phone', this.value.trim())) {
            showFieldError(this, errorMessages.phone);
        }
    });

    // 注册表单验证
    document.getElementById('reg-username').addEventListener('blur', function() {
        if (this.value && !validateField('username', this.value.trim())) {
            showFieldError(this, errorMessages.username);
        }
    });

    document.getElementById('reg-password').addEventListener('blur', function() {
        if (this.value && !validateField('password', this.value)) {
            showFieldError(this, errorMessages.password);
        }
    });

    document.getElementById('reg-password').addEventListener('input', function() {
        // 更新密码强度指示器
        const strength = getPasswordStrength(this.value);
        const strengthEl = this.closest('.input-group').querySelector('.password-strength');
        if (strengthEl) {
            strengthEl.className = `password-strength ${strength}`;
        }
    });

    document.getElementById('reg-confirm-password').addEventListener('blur', function() {
        const password = document.getElementById('reg-password').value;
        if (this.value && this.value !== password) {
            showFieldError(this, errorMessages.passwordMismatch);
        }
    });

    document.getElementById('reg-email').addEventListener('blur', function() {
        if (this.value && !validateField('email', this.value.trim())) {
            showFieldError(this, errorMessages.email);
        }
    });

    document.getElementById('reg-phone').addEventListener('blur', function() {
        if (this.value && !validateField('phone', this.value.trim())) {
            showFieldError(this, errorMessages.phone);
        }
    });

    document.getElementById('reg-nickname').addEventListener('blur', function() {
        if (this.value && !validateField('nickname', this.value.trim())) {
            showFieldError(this, errorMessages.nickname);
        }
    });

    // 输入时清除错误
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });

    // 回车登录
    document.getElementById('login-password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loginWithPassword();
    });

    document.getElementById('login-email-code').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loginWithEmail();
    });

    document.getElementById('login-phone-code').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loginWithPhone();
    });
}
