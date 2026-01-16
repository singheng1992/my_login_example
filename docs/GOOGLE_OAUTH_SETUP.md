# Google OAuth 登录配置指南

## 问题描述

如果在 Google OAuth 登录时看到以下错误：

```
错误 400： redirect_uri_mismatch
禁止访问：此应用的请求无效
无法登录，因为此应用发送的请求无效。
```

这说明 Google Cloud Console 中配置的 `Authorized redirect URI` 与代码中的不匹配。

## 解决方案

### 步骤 1: 在 Google Cloud Console 创建 OAuth 2.0 凭证

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 进入 **API和服务** → **凭据**
4. 点击 **创建凭据** → **OAuth 客户端 ID**
5. 如果是首次创建，需要先配置 **OAuth 同意屏幕**：
   - 选择 **外部** 用户类型
   - 填写应用名称、用户支持电子邮件等必填信息
   - 保存并继续

### 步骤 2: 配置 OAuth 客户端

1. 应用类型选择 **Web 应用**
2. 填写名称：`Login Demo`
3. **已获授权的重定向 URI** 添加：
   ```
   http://localhost:8000/api/auth/oauth/google/callback
   ```
4. 点击 **创建**

### 步骤 3: 获取凭证

创建后会显示 **客户端 ID** 和 **客户端密钥**：
- 复制 **客户端 ID**
- 复制 **客户端密钥**

### 步骤 4: 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# Google OAuth
OAUTH_GOOGLE_CLIENT_ID=你的客户端_ID
OAUTH_GOOGLE_CLIENT_SECRET=你的客户端密钥
```

### 步骤 5: 确保 SERVER_BASE_URL 正确配置

在 `backend/.env` 文件中确保：

```bash
SERVER_BASE_URL=http://localhost:8000
```

**重要：**
- Google 的 **Authorized redirect URI** 必须是: `http://localhost:8000/api/auth/oauth/google/callback`
- `.env` 中的 `SERVER_BASE_URL` 必须是: `http://localhost:8000`
- 两者必须完全匹配！

## 生产环境配置

生产环境需要修改为实际的域名：

### Google Cloud Console 配置

在 **已获授权的重定向 URI** 中添加：

```
https://api.yourdomain.com/api/auth/oauth/google/callback
```

### 环境变量配置

```bash
SERVER_BASE_URL=https://api.yourdomain.com
OAUTH_GOOGLE_CLIENT_ID=生产环境客户端_ID
OAUTH_GOOGLE_CLIENT_SECRET=生产环境客户端密钥
```

## 验证配置

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试 OAuth 授权 URL

```bash
curl http://localhost:8000/api/auth/oauth/google
```

应该返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
    "state": "..."
  }
}
```

### 3. 检查 redirect_uri

从返回的 `auth_url` 中，检查 `redirect_uri` 参数是否为：

```
http://localhost:8000/api/auth/oauth/google/callback
```

## 常见问题

### 1. redirect_uri 不匹配

**问题：** Google 提示 redirect_uri_mismatch

**解决：**
- 确认 Google Cloud Console 中的 **已获授权的重定向 URI**
- 确认 `.env` 中的 `SERVER_BASE_URL`
- 两者必须完全匹配（包括协议 http/https、域名、端口、路径）

### 2. 端口号错误

**问题：** 本地开发使用 8000 端口，但配置了其他端口

**解决：**
- 前端端口：`http://localhost:8080`（用户访问）
- 后端端口：`http://localhost:8000`（API 服务器）
- OAuth 回调必须指向后端：`http://localhost:8000/api/auth/oauth/google/callback`

### 3. HTTPS 问题

**问题：** 本地开发使用 HTTP，但生产环境配置了 HTTPS

**解决：**
- 开发环境使用 HTTP (`http://localhost:8000`)
- 生产环境使用 HTTPS (`https://api.yourdomain.com`)
- 为不同环境创建不同的 OAuth 客户端 ID

### 4. OAuth 同意屏幕未配置

**问题：** 创建 OAuth 客户端时提示配置同意屏幕

**解决：**
1. 进入 **API和服务** → **OAuth 同意屏幕**
2. 选择 **外部** 用户类型
3. 填写必填信息：
   - 应用名称
   - 用户支持电子邮件
   - 开发者联系信息
4. 保存并发布

## Google OAuth 与 GitHub OAuth 的区别

| 特性 | GitHub OAuth | Google OAuth |
|------|-------------|--------------|
| Authorization URL | `/login/oauth/authorize` | `/o/oauth2/v2/auth` |
| Token URL | `/login/oauth/access_token` | `/token` |
| User Info URL | `/api.github.com/user` | `/oauth2/v2/userinfo` |
| Redirect URI 传递方式 | URL 参数 | URL 参数 |
| Scope | `user:email` | `openid email profile` |

## 调试技巧

### 查看实际生成的 redirect_uri

在 `backend/app/services/oauth_service.py` 中添加调试日志：

```python
def get_authorization_url(self, provider: str, redirect_uri: str, state: str) -> str:
    print(f"[DEBUG] {provider} redirect_uri: {redirect_uri}")  # 添加这行
    # ... 原有代码
```

启动服务后会在控制台打印实际的 redirect_uri，将其与 Google Cloud Console 配置对比。

### 查看错误详情

Google OAuth 错误页面会包含详细的 `redirect_uri_mismatch` 信息，显示：
- 请求的 redirect_uri
- 允许的 redirect_uri 列表

对比两者，找出不匹配的地方。
