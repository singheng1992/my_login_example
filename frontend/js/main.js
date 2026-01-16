/**
 * 主入口文件
 */

// ==================== 应用初始化 ====================

/**
 * 初始化应用
 */
function initApp() {
    // 先处理OAuth回调（需要在checkLoginStatus之前）
    handleOAuthCallback();

    // 初始化认证模块
    initAuthModule();

    // 初始化用户模块
    initUserModule();

    // 检查登录状态
    checkLoginStatus();
}

/**
 * 检查登录状态
 */
function checkLoginStatus() {
    const token = getToken();

    if (token) {
        // 已登录，加载用户信息并切换到用户中心
        loadUserProfile().then(() => {
            switchView('user-view');
        }).catch(() => {
            // token无效，切换到登录页
            switchView('auth-view');
        });
    } else {
        // 未登录，显示登录页
        switchView('auth-view');
    }
}

// ==================== 页面加载完成后初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

// ==================== 全局错误处理 ====================

window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise错误:', event.reason);
});

window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
});
