/**
 * 用户模块 - 用户中心逻辑
 */

// ==================== 加载用户信息 ====================

/**
 * 加载用户资料
 */
async function loadUserProfile() {
    const token = getToken();
    if (!token) {
        return;
    }

    try {
        // 从API获取最新用户信息
        const response = await get(API_ENDPOINTS.USER_PROFILE);
        const userInfo = response.data;
        saveUserInfo(userInfo);
        updateUserInfoUI(userInfo);
    } catch (error) {
        console.error('获取用户信息失败:', error);
        // 如果API调用失败，尝试使用本地缓存
        const cachedUserInfo = getUserInfo();
        if (cachedUserInfo) {
            updateUserInfoUI(cachedUserInfo);
        }
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
}
