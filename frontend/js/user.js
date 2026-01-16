/**
 * 用户模块 - 用户中心逻辑
 */

// ==================== 加载用户信息 ====================

/**
 * 加载用户资料
 * @returns {Promise<Object|null>} 用户信息对象
 */
async function loadUserProfile() {
    const token = getToken();
    if (!token) {
        return null;
    }

    try {
        // 从API获取最新用户信息
        const response = await get(API_ENDPOINTS.USER_PROFILE);
        const userInfo = response.data;
        saveUserInfo(userInfo);
        updateUserInfoUI(userInfo);
        return userInfo;
    } catch (error) {
        console.error('获取用户信息失败:', error);
        // 如果API调用失败，尝试使用本地缓存
        const cachedUserInfo = getUserInfo();
        if (cachedUserInfo) {
            updateUserInfoUI(cachedUserInfo);
            return cachedUserInfo;
        }
        return null;
    }
}

/**
 * 更新用户信息UI
 */
function updateUserInfoUI(userInfo) {
    // 更新导航栏头像
    const navAvatar = document.getElementById('nav-avatar');
    if (navAvatar) {
        if (userInfo.avatar_url) {
            navAvatar.src = userInfo.avatar_url.startsWith('http')
                ? userInfo.avatar_url
                : `${API_BASE_URL.replace('/api', '')}${userInfo.avatar_url}`;
        }
    }

    // 更新用户中心信息
    const userAvatar = document.getElementById('user-avatar');
    if (userAvatar) {
        if (userInfo.avatar_url) {
            userAvatar.src = userInfo.avatar_url.startsWith('http')
                ? userInfo.avatar_url
                : `${API_BASE_URL.replace('/api', '')}${userInfo.avatar_url}`;
        }
    }

    // 昵称
    const nicknameEl = document.getElementById('user-nickname');
    if (nicknameEl) {
        nicknameEl.textContent = userInfo.nickname || '未设置昵称';
    }

    // 用户名
    const usernameEl = document.getElementById('user-username');
    if (usernameEl) {
        usernameEl.textContent = userInfo.username ? `@${userInfo.username}` : '--';
    }

    // 邮箱
    const emailEl = document.getElementById('user-email');
    if (emailEl) {
        emailEl.textContent = userInfo.email
            ? maskSensitiveInfo(userInfo.email, 'email')
            : '未设置';
    }

    // 手机号
    const phoneEl = document.getElementById('user-phone');
    if (phoneEl) {
        phoneEl.textContent = userInfo.phone
            ? maskSensitiveInfo(userInfo.phone, 'phone')
            : '未设置';
    }

    // 注册时间
    const createdEl = document.getElementById('user-created');
    if (createdEl) {
        createdEl.textContent = userInfo.created_at
            ? formatDate(userInfo.created_at)
            : '--';
    }
}

// ==================== 初始化 ====================

/**
 * 初始化用户模块
 */
function initUserModule() {
    // 退出按钮
    document.getElementById('btn-logout').addEventListener('click', logout);

    // 初始化邮箱补全模态框
    initEmailCompletionModal();
}


// ==================== 更新邮箱 ====================

/**
 * 发送邮箱验证码（用于更新邮箱）
 */
async function sendEmailCodeForUpdate() {
    const emailInput = document.getElementById('new-email');
    const email = emailInput.value.trim();

    if (!email) {
        showToast('请输入新邮箱地址', 'error');
        return;
    }

    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showToast('邮箱格式不正确', 'error');
        return;
    }

    try {
        await post(API_ENDPOINTS.SEND_EMAIL, { identifier: email });
        showToast('验证码已发送到新邮箱，请注意查收', 'success');

        // 启动倒计时
        startEmailCountdown();
    } catch (error) {
        showToast(error.message || '发送失败，请重试', 'error');
    }
}

/**
 * 更新邮箱
 */
async function updateEmail() {
    const emailInput = document.getElementById('new-email');
    const codeInput = document.getElementById('email-code');

    const email = emailInput.value.trim();
    const code = codeInput.value.trim();

    if (!email) {
        showToast('请输入新邮箱地址', 'error');
        return;
    }

    if (!code) {
        showToast('请输入验证码', 'error');
        return;
    }

    try {
        const response = await put(API_ENDPOINTS.USER_UPDATE_EMAIL, {
            email: email,
            code: code
        });

        showToast('邮箱更新成功', 'success');

        // 更新本地存储的用户信息
        saveUserInfo(response.data);

        // 更新 UI
        updateUserInfoUI(response.data);

        // 清空表单
        emailInput.value = '';
        codeInput.value = '';

        // 关闭模态框（如果有）
        const modal = document.getElementById('update-email-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    } catch (error) {
        showToast(error.message || '更新失败，请重试', 'error');
    }
}

/**
 * 启动邮箱验证码倒计时
 */
function startEmailCountdown() {
    const sendBtn = document.getElementById('btn-send-email-code');
    if (!sendBtn) return;

    let seconds = COUNTDOWN_SECONDS;
    sendBtn.disabled = true;
    sendBtn.textContent = `${seconds}秒后重试`;

    const timer = setInterval(() => {
        seconds--;
        if (seconds <= 0) {
            clearInterval(timer);
            sendBtn.disabled = false;
            sendBtn.textContent = '发送验证码';
        } else {
            sendBtn.textContent = `${seconds}秒后重试`;
        }
    }, 1000);
}


// ==================== 邮箱补全模态框 ====================

/**
 * 显示邮箱补全模态框
 */
function showEmailCompletionModal() {
    const modal = document.getElementById('email-completion-modal');
    if (modal) {
        modal.classList.remove('hidden');
        // 禁用页面滚动
        document.body.style.overflow = 'hidden';
        // 清空之前的输入
        const emailInput = document.getElementById('completion-email');
        const codeInput = document.getElementById('completion-email-code');
        if (emailInput) emailInput.value = '';
        if (codeInput) codeInput.value = '';
        // 清除错误提示
        document.querySelectorAll('#email-completion-modal .error-message').forEach(el => {
            el.textContent = '';
        });
        document.querySelectorAll('#email-completion-modal input.error').forEach(el => {
            el.classList.remove('error');
        });
    }
}

/**
 * 关闭邮箱补全模态框
 */
function closeEmailCompletionModal() {
    const modal = document.getElementById('email-completion-modal');
    if (modal) {
        modal.classList.add('hidden');
        // 恢复页面滚动
        document.body.style.overflow = '';
    }
}

/**
 * 发送补全邮箱验证码
 */
async function sendCompletionEmailCode() {
    const emailInput = document.getElementById('completion-email');
    const email = emailInput.value.trim();

    if (!email) {
        showCompletionFieldError(emailInput, '请输入邮箱地址');
        return;
    }

    // 验证邮箱格式
    if (!validateField('email', email)) {
        showCompletionFieldError(emailInput, errorMessages.email);
        return;
    }

    const sendBtn = document.getElementById('btn-send-completion-email');
    sendBtn.disabled = true;
    sendBtn.textContent = '发送中...';

    try {
        await post(API_ENDPOINTS.SEND_EMAIL, { identifier: email });
        toast.success('验证码已发送到您的邮箱');

        // 启动倒计时
        let seconds = COUNTDOWN_SECONDS;
        sendBtn.disabled = true;
        sendBtn.textContent = `${seconds}秒后重试`;

        const timer = setInterval(() => {
            seconds--;
            if (seconds <= 0) {
                clearInterval(timer);
                sendBtn.disabled = false;
                sendBtn.textContent = '发送验证码';
            } else {
                sendBtn.textContent = `${seconds}秒后重试`;
            }
        }, 1000);
    } catch (error) {
        toast.error(error.message || '发送失败');
        sendBtn.disabled = false;
        sendBtn.textContent = '发送验证码';
    }
}

/**
 * 提交补全邮箱
 */
async function submitCompletionEmail() {
    const emailInput = document.getElementById('completion-email');
    const codeInput = document.getElementById('completion-email-code');
    const submitBtn = document.getElementById('btn-submit-completion-email');

    const email = emailInput.value.trim();
    const code = codeInput.value.trim();

    // 验证
    let isValid = true;

    if (!email) {
        showCompletionFieldError(emailInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('email', email)) {
        showCompletionFieldError(emailInput, errorMessages.email);
        isValid = false;
    }

    if (!code) {
        showCompletionFieldError(codeInput, errorMessages.required);
        isValid = false;
    } else if (!validateField('code', code)) {
        showCompletionFieldError(codeInput, errorMessages.code);
        isValid = false;
    }

    if (!isValid) return;

    // 禁用按钮
    submitBtn.disabled = true;
    submitBtn.textContent = '提交中...';

    try {
        const response = await put(API_ENDPOINTS.USER_UPDATE_EMAIL, {
            email: email,
            code: code
        });

        // 检查是否是账号关联的情况
        const userId = response.data.id;
        const currentUserId = getUserInfo()?.id;

        if (userId !== currentUserId) {
            // 账号已关联，使用目标账号的信息
            toast.success('邮箱已绑定，账号已关联');

            // 更新本地存储的用户信息
            saveUserInfo(response.data);

            // 更新 UI
            updateUserInfoUI(response.data);

            // 关闭模态框
            closeEmailCompletionModal();
        } else {
            toast.success('邮箱添加成功');

            // 更新本地存储的用户信息
            saveUserInfo(response.data);

            // 更新 UI
            updateUserInfoUI(response.data);

            // 关闭模态框
            closeEmailCompletionModal();
        }

    } catch (error) {
        toast.error(error.message || '添加失败');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '绑定邮箱';
    }
}

/**
 * 显示补全模态框字段错误
 */
function showCompletionFieldError(input, message) {
    const group = input.closest('.input-group');
    const errorEl = group.querySelector('.error-message');
    input.classList.add('error');
    if (errorEl) {
        errorEl.textContent = message;
    }
}

/**
 * 初始化邮箱补全模态框事件
 */
function initEmailCompletionModal() {
    // 发送验证码按钮
    const sendBtn = document.getElementById('btn-send-completion-email');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendCompletionEmailCode);
    }

    // 提交按钮
    const submitBtn = document.getElementById('btn-submit-completion-email');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitCompletionEmail);
    }

    // 阻止 ESC 键关闭模态框
    document.addEventListener('keydown', function escHandler(e) {
        const modal = document.getElementById('email-completion-modal');
        if (modal && !modal.classList.contains('hidden') && e.key === 'Escape') {
            e.preventDefault();
            e.stopPropagation();
        }
    }, { capture: true });

    // 输入时清除错误
    const emailInput = document.getElementById('completion-email');
    const codeInput = document.getElementById('completion-email-code');

    if (emailInput) {
        emailInput.addEventListener('input', function() {
            this.classList.remove('error');
            const errorEl = this.closest('.input-group').querySelector('.error-message');
            if (errorEl) errorEl.textContent = '';
        });
    }

    if (codeInput) {
        codeInput.addEventListener('input', function() {
            this.classList.remove('error');
            const errorEl = this.closest('.input-group').querySelector('.error-message');
            if (errorEl) errorEl.textContent = '';
        });
    }
}
