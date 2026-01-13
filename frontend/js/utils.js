/**
 * 工具函数
 */

// ==================== 表单验证 ====================

/**
 * 验证规则
 */
const validators = {
    // 用户名：3-20字符，字母数字下划线
    username: (val) => /^[a-zA-Z0-9_]{3,20}$/.test(val),
    // 密码：8-32字符，必须包含字母和数字
    password: (val) => /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,32}$/.test(val),
    // 邮箱格式
    email: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val),
    // 手机号：11位数字
    phone: (val) => /^1[3-9]\d{9}$/.test(val),
    // 验证码：6位数字
    code: (val) => /^\d{6}$/.test(val),
    // 昵称：2-20字符
    nickname: (val) => val === '' || /^.{2,20}$/.test(val)
};

/**
 * 验证错误提示
 */
const errorMessages = {
    username: '用户名必须是3-20位的字母、数字或下划线',
    password: '密码必须8-32位，包含字母和数字',
    passwordMismatch: '两次密码输入不一致',
    email: '请输入有效的邮箱地址',
    phone: '请输入有效的手机号',
    code: '请输入6位验证码',
    nickname: '昵称必须是2-20个字符',
    required: '此项为必填项'
};

/**
 * 验证单个字段
 */
function validateField(type, value) {
    if (validators[type]) {
        return validators[type](value);
    }
    return true;
}

/**
 * 获取错误消息
 */
function getErrorMessage(type) {
    return errorMessages[type] || '输入格式不正确';
}

/**
 * 验证密码强度
 */
function getPasswordStrength(password) {
    if (!password) return 'weak';

    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[@$!%*?&]/.test(password)) score++;

    if (score <= 2) return 'weak';
    if (score <= 4) return 'medium';
    return 'strong';
}

// ==================== HTTP请求 ====================

/**
 * 统一请求函数
 */
async function request(url, options = {}) {
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };

    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            ...options,
            headers: { ...headers, ...options.headers },
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.message || '请求失败');
        }

        return data;
    } catch (error) {
        clearTimeout(timeoutId);

        if (error.name === 'AbortError') {
            throw new Error('请求超时，请检查网络连接');
        }

        throw error;
    }
}

/**
 * GET请求
 */
function get(url, options = {}) {
    return request(url, { ...options, method: 'GET' });
}

/**
 * POST请求
 */
function post(url, data, options = {}) {
    return request(url, {
        ...options,
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * PUT请求
 */
function put(url, data, options = {}) {
    return request(url, {
        ...options,
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// ==================== Toast消息提示 ====================

const toast = {
    container: null,
    currentToast: null,
    hideTimer: null,

    /**
     * 初始化容器
     */
    init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    /**
     * 显示toast
     */
    show(type, message, duration = 3000) {
        this.init();

        // 移除当前的toast
        if (this.currentToast) {
            this.hide();
        }

        const icons = {
            success: '✓',
            error: '✕',
            loading: '⟳'
        };

        const toastEl = document.createElement('div');
        toastEl.className = `toast ${type}`;
        toastEl.innerHTML = `
            <span class="toast-icon">${icons[type] || 'ℹ'}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="toast.hide()">×</button>
        `;

        this.container.appendChild(toastEl);
        this.currentToast = toastEl;

        // 自动隐藏
        if (duration > 0 && type !== 'loading') {
            this.hideTimer = setTimeout(() => this.hide(), duration);
        }

        return toastEl;
    },

    /**
     * 成功提示
     */
    success(message, duration) {
        return this.show('success', message, duration);
    },

    /**
     * 错误提示
     */
    error(message, duration) {
        return this.show('error', message, duration);
    },

    /**
     * 加载提示
     */
    loading(message) {
        return this.show('loading', message, 0);
    },

    /**
     * 隐藏toast
     */
    hide() {
        if (this.hideTimer) {
            clearTimeout(this.hideTimer);
            this.hideTimer = null;
        }

        if (this.currentToast) {
            this.currentToast.classList.add('hiding');
            setTimeout(() => {
                if (this.currentToast && this.currentToast.parentNode) {
                    this.currentToast.parentNode.removeChild(this.currentToast);
                }
                this.currentToast = null;
            }, 300);
        }
    }
};

// ==================== 本地存储 ====================

/**
 * 保存token
 */
function saveToken(token) {
    localStorage.setItem(STORAGE_KEYS.TOKEN, token);
}

/**
 * 获取token
 */
function getToken() {
    return localStorage.getItem(STORAGE_KEYS.TOKEN);
}

/**
 * 移除token
 */
function removeToken() {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_INFO);
}

/**
 * 保存用户信息
 */
function saveUserInfo(userInfo) {
    localStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(userInfo));
}

/**
 * 获取用户信息
 */
function getUserInfo() {
    const info = localStorage.getItem(STORAGE_KEYS.USER_INFO);
    return info ? JSON.parse(info) : null;
}

// ==================== 表单操作 ====================

/**
 * 显示字段错误
 */
function showFieldError(input, message) {
    const group = input.closest('.input-group');
    const errorEl = group.querySelector('.error-message');
    input.classList.add('error');
    if (errorEl) {
        errorEl.textContent = message;
    }
}

/**
 * 清除字段错误
 */
function clearFieldError(input) {
    const group = input.closest('.input-group');
    const errorEl = group.querySelector('.error-message');
    input.classList.remove('error');
    if (errorEl) {
        errorEl.textContent = '';
    }
}

/**
 * 清除所有错误
 */
function clearAllErrors(container) {
    container.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    container.querySelectorAll('input.error').forEach(el => el.classList.remove('error'));
}

/**
 * 禁用表单
 */
function disableForm(form, disabled = true) {
    form.querySelectorAll('button, input').forEach(el => {
        el.disabled = disabled;
    });
}

// ==================== 倒计时 ====================

/**
 * 倒计时管理器
 */
const countdown = {
    timers: new Map(),

    /**
     * 开始倒计时
     */
    start(buttonId, seconds = COUNTDOWN_SECONDS) {
        const button = document.getElementById(buttonId);
        if (!button) return;

        // 清除已有的倒计时
        this.stop(buttonId);

        button.disabled = true;
        button.textContent = `${seconds}s后重发`;

        const timer = setInterval(() => {
            seconds--;
            if (seconds <= 0) {
                this.stop(buttonId);
                button.disabled = false;
                button.textContent = '发送验证码';
            } else {
                button.textContent = `${seconds}s后重发`;
            }
        }, 1000);

        this.timers.set(buttonId, timer);
    },

    /**
     * 停止倒计时
     */
    stop(buttonId) {
        const timer = this.timers.get(buttonId);
        if (timer) {
            clearInterval(timer);
            this.timers.delete(buttonId);
        }
    },

    /**
     * 停止所有倒计时
     */
    stopAll() {
        this.timers.forEach((timer, buttonId) => {
            clearInterval(timer);
            const button = document.getElementById(buttonId);
            if (button) {
                button.disabled = false;
                button.textContent = '发送验证码';
            }
        });
        this.timers.clear();
    }
};

// ==================== 视图切换 ====================

/**
 * 切换视图
 */
function switchView(viewId) {
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    const targetView = document.getElementById(viewId);
    if (targetView) {
        targetView.classList.add('active');
    }
}

/**
 * 切换标签页
 */
function switchTab(tabId) {
    // 更新标签按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabId) {
            btn.classList.add('active');
        }
    });

    // 更新标签内容显示
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        if (content.dataset.tab === tabId) {
            content.classList.add('active');
        }
    });
}

// ==================== 格式化 ====================

/**
 * 格式化日期
 */
function formatDate(dateString) {
    if (!dateString) return '--';

    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
}

/**
 * 隐藏敏感信息
 */
function maskSensitiveInfo(value, type) {
    if (!value) return '--';

    switch (type) {
        case 'email':
            const [name, domain] = value.split('@');
            if (name.length <= 2) return value;
            return `${name.slice(0, 2)}***@${domain}`;
        case 'phone':
            return value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
        default:
            return value;
    }
}
