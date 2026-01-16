# GitHub OAuth 登录配置指南

## 问题描述

如果在 GitHub OAuth 登录时看到以下错误：

```
Be careful!

The redirect_uri is not associated with this application.

The application might be misconfigured or could be trying to redirect you to a website you weren't expecting.
```

这说明 GitHub OAuth 应用配置中的 `redirect_uri` 与代码中的不匹配。

## 解决方案

### 步骤 1: 在 GitHub 创建 OAuth 应用

1. 访问 GitHub: https://github.com/settings/developers
2. 点击 "OAuth Apps" → "New OAuth App"
3. 填写应用信息：

| 字段 | 值 | 说明 |
|------|-----|------|
| Application name | Login Demo | 应用名称 |
| Homepage URL | http://localhost:8080 | 前端首页地址 |
| Application description | 登录演示应用 | 应用描述 |
| Authorization callback URL | **http://localhost:8000/api/auth/oauth/github/callback** | **重要：必须完全匹配** |

### 步骤 2: 获取凭证

创建应用后，复制以下信息：
- Client ID
- Client Secret（点击 Generate new client secret 生成）

### 步骤 3: 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# GitHub OAuth
OAUTH_GITHUB_CLIENT_ID=你的_Client_ID
OAUTH_GITHUB_CLIENT_SECRET=你的_Client_Secret
```

### 步骤 4: 确保 SERVER_BASE_URL 正确配置

在 `backend/.env` 文件中确保：

```bash
SERVER_BASE_URL=http://localhost:8000
```

**重要：**
- GitHub 的 `Authorization callback URL` 必须是: `http://localhost:8000/api/auth/oauth/github/callback`
- `.env` 中的 `SERVER_BASE_URL` 必须是: `http://localhost:8000`
- 两者必须完全匹配！

## 生产环境配置

生产环境需要修改为实际的域名：

### GitHub OAuth 应用配置

| 字段 | 值 |
|------|-----|
| Homepage URL | https://yourdomain.com |
| Authorization callback URL | **https://api.yourdomain.com/api/auth/oauth/github/callback** |

### 环境变量配置

```bash
SERVER_BASE_URL=https://api.yourdomain.com
OAUTH_GITHUB_CLIENT_ID=生产环境_Client_ID
OAUTH_GITHUB_CLIENT_SECRET=生产环境_Client_Secret
```

## 验证配置

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试 OAuth 授权 URL

```bash
curl http://localhost:8000/api/auth/oauth/github
```

应该返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "auth_url": "https://github.com/login/oauth/authorize?client_id=..."
  }
}
```

### 3. 检查 redirect_uri

从返回的 `auth_url` 中复制并解码，检查 `redirect_uri` 参数是否为：

```
http://localhost:8000/api/auth/oauth/github/callback
```

## 常见问题

### 1. redirect_uri 不匹配

**问题：** GitHub 提示 redirect_uri 未关联

**解决：** 确保 GitHub OAuth 应用中的 `Authorization callback URL` 与 `.env` 中的 `SERVER_BASE_URL` 一致。

### 2. 端口号错误

**问题：** 前端使用 8080，但后端配置为 8000

**解决：**
- 前端端口：`http://localhost:8080`（用户访问）
- 后端端口：`http://localhost:8000`（API 服务器）
- OAuth 回调必须指向后端：`http://localhost:8000/api/auth/oauth/github/callback`

### 3. HTTPS 问题

**问题：** 本地开发使用 HTTP，但 GitHub 应用配置为 HTTPS

**解决：** 开发环境使用 HTTP，生产环境使用 HTTPS。可以为不同环境创建不同的 GitHub OAuth 应用。

## 调试技巧

### 查看实际生成的 redirect_uri

在 `backend/app/api/auth.py` 中添加调试日志：

```python
@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    try:
        redirect_uri = f"{settings.SERVER_BASE_URL}/api/auth/oauth/{provider}/callback"
        print(f"生成的 redirect_uri: {redirect_uri}")  # 添加这行
        state = "random_state_string"
        auth_url = oauth_service.get_authorization_url(provider, redirect_uri, state)
        return ApiResponse(data={"auth_url": auth_url})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

启动服务后会在控制台打印实际的 redirect_uri，将其与 GitHub OAuth 应用配置对比。
