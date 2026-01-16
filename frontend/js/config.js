/**
 * API配置
 */

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api';

// API端点
const API_ENDPOINTS = {
    // 认证相关
    REGISTER: '/auth/register',
    LOGIN_PASSWORD: '/auth/login/password',
    LOGIN_EMAIL: '/auth/login/email',
    LOGIN_SMS: '/auth/login/sms',
    SEND_EMAIL: '/auth/send-email',
    SEND_SMS: '/auth/send-sms',
    OAUTH: '/auth/oauth',
    OAUTH_CALLBACK: '/auth/oauth',
    LOGOUT: '/auth/logout',

    // 用户相关
    USER_PROFILE: '/user/profile',
    USER_UPDATE: '/user/profile',
    USER_UPDATE_EMAIL: '/user/email',
    USER_AVATAR: '/user/avatar'
};

// 本地存储键名
const STORAGE_KEYS = {
    TOKEN: 'token',
    USER_INFO: 'userInfo'
};

// OAuth提供商
const OAUTH_PROVIDERS = [
    { id: 'github', name: 'GitHub' },
    { id: 'google', name: 'Google' },
    { id: 'dingtalk', name: '钉钉' },
    { id: 'feishu', name: '飞书' },
    { id: 'wechat', name: '微信' }
];

// 验证码倒计时时间（秒）
const COUNTDOWN_SECONDS = 60;

// 请求超时时间（毫秒）
const REQUEST_TIMEOUT = 10000;
