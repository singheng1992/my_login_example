const API_BASE_URL = 'http://localhost:8000';

const config = {
    apiBaseUrl: API_BASE_URL,
    oauthProviders: {
        github: `${API_BASE_URL}/api/auth/oauth/github`,
        google: `${API_BASE_URL}/api/auth/oauth/google`,
        wechat: `${API_BASE_URL}/api/auth/oauth/wechat`,
        dingtalk: `${API_BASE_URL}/api/auth/oauth/dingtalk`,
        feishu: `${API_BASE_URL}/api/auth/oauth/feishu`
    }
};
