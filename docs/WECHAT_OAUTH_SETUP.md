# 微信 OAuth 登录配置指南

## 前置条件

微信开放平台 OAuth 登录需要**企业认证**，个人开发者无法申请。

**重要提醒**：
- 微信开放平台需要企业认证（300元/年）
- 需要有已备案的域名
- 个人开发者无法使用微信网站扫码登录

## 微信 OAuth 两种方式

### 方式一：微信开放平台（网站扫码登录）

适用于 PC 网站扫码登录。

- 授权 URL：`https://open.weixin.qq.com/connect/qrconnect`
- Scope：`snsapi_login`
- 用户使用微信扫描二维码登录

### 方式二：微信公众平台（网页授权）

适用于微信内打开的网页。

- 授权 URL：`https://open.weixin.qq.com/connect/oauth2/authorize`
- Scope：`snsapi_userinfo`（获取用户信息）或 `snsapi_base`（静默授权）
- 必须在微信客户端内打开

## 方式一：微信开放平台配置步骤

### 步骤 1: 注册微信开放平台

1. 访问 [微信开放平台](https://open.weixin.qq.com/)
2. 注册开发者账号（需要企业认证）
3. 完成企业认证（300元/年）

### 步骤 2: 创建网站应用

1. 进入 **管理中心** → **网站应用**
2. 点击 **创建网站应用**
3. 填写应用信息：
   - 应用名称：`Login Demo`
   - 应用简介：登录演示应用
   - 应用官网：`https://yourdomain.com`
   - **授权回调域**：`yourdomain.com`（不要带 http:// 或路径）

### 步骤 3: 等待审核

提交后等待微信审核（通常 1-7 个工作日）。

### 步骤 4: 获取凭证

审核通过后，获取：
- **AppID**：应用唯一标识
- **AppSecret**：应用密钥

### 步骤 5: 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# 微信 OAuth
OAUTH_WECHAT_APP_ID=你的_AppID
OAUTH_WECHAT_APP_SECRET=你的_AppSecret
```

### 步骤 6: 确保 SERVER_BASE_URL 正确配置

```bash
SERVER_BASE_URL=http://localhost:8000  # 开发环境
# SERVER_BASE_URL=https://api.yourdomain.com  # 生产环境
```

**重要：**
- 微信的 **授权回调域** 必须是: `yourdomain.com`（不带协议）
- `.env` 中的 `SERVER_BASE_URL` 可以是: `http://localhost:8000`
- 回调完整 URL 会自动拼接为: `http://localhost:8000/api/auth/oauth/wechat/callback`

## 生产环境配置

### 微信开放平台配置

**授权回调域**：
```
api.yourdomain.com
```

**注意**：
- 不要带 `https://`
- 不要带端口号
- 不要带路径

### 环境变量配置

```bash
SERVER_BASE_URL=https://api.yourdomain.com
OAUTH_WECHAT_APP_ID=生产环境_AppID
OAUTH_WECHAT_APP_SECRET=生产环境_AppSecret
```

## 验证配置

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. 测试 OAuth 授权 URL

```bash
curl http://localhost:8000/api/auth/oauth/wechat
```

应该返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "auth_url": "https://open.weixin.qq.com/connect/qrconnect?appid=...",
    "state": "..."
  }
}
```

### 3. 检查 auth_url

从返回的 `auth_url` 中验证：
- `appid` 参数存在
- `redirect_uri` 已进行 URL 编码（例如：`http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fauth%2Foauth%2Fwechat%2Fcallback`）
- `response_type=code`
- `scope=snsapi_login`
- `state` 参数存在

## 微信 OAuth 与其他 OAuth 的区别

| 特性 | GitHub OAuth | Google OAuth | 微信 OAuth |
|------|-------------|--------------|-----------|
| 授权 URL | `/login/oauth/authorize` | `/o/oauth2/v2/auth` | `/connect/qrconnect` |
| Token URL | `/login/oauth/access_token` | `/token` | `/sns/oauth2/access_token` |
| User Info URL | `/api.github.com/user` | `/oauth2/v2/userinfo` | `/sns/userinfo` |
| Client ID 参数名 | `client_id` | `client_id` | `appid` |
| redirect_uri | 原样使用 | 原样使用 | **必须 URL 编码** |
| Token 请求方式 | POST | POST | GET |
| 用户 ID | `id` | `id` | `unionid` 或 `openid` |
| 邮箱 | ✅ 提供 | ✅ 提供 | ❌ 不提供 |

## 微信用户信息说明

微信返回的用户信息：

```json
{
  "openid": "oXXXXXX",
  "unionid": "uXXXXXX",  // 仅在开放平台账号绑定应用后返回
  "nickname": "微信昵称",
  "sex": 1,  // 1=男性, 2=女性, 0=未知
  "province": "广东",
  "city": "深圳",
  "country": "中国",
  "headimgurl": "http://thirdwx.qlogo.cn/...",
  "privilege": [],
  "language": "zh_CN"
}
```

**注意事项**：
- `unionid` 只有在开放平台账号下绑定该应用后才返回
- 如果没有 `unionid`，使用 `openid` 作为用户唯一标识
- 微信**不提供用户邮箱**，只能获取昵称和头像

## 常见问题

### 1. redirect_uri 参数错误

**问题**：微信提示 `redirect_uri 参数错误`

**解决**：
- 检查微信开放平台的 **授权回调域** 配置
- 确保回调域名与配置一致（不包括协议和路径）
- 生产环境必须使用 HTTPS

### 2: redirect_uri 域名与后台配置不一致

**问题**：微信提示 `redirect_uri 域名与后台配置不一致`

**解决**：
- 确认微信开放平台配置的 **授权回调域**
- 确保 `.env` 中的 `SERVER_BASE_URL` 的域名与之一致
- 域名必须完全匹配（不包括协议和端口）

### 3: code 无效

**问题**：获取用户信息时提示 `code 无效`

**解决**：
- `code` 只能使用一次，且 5 分钟内有效
- 不要重复使用同一个 `code`
- 确保 state 验证通过后再使用 code

### 4: 个人开发者无法申请

**问题**：没有企业资质如何使用微信登录

**解决方案**：
1. 使用测试号（仅限开发测试，无法正式上线）
   - 微信公众平台测试号：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login
   - 但测试号只支持微信内网页授权，不支持扫码登录

2. 使用其他 OAuth 方案
   - GitHub OAuth（免费，推荐）
   - Google OAuth（免费）
   - 钉钉/飞书（需要企业）

## 微信内网页授权（方式二）

如果你的应用主要在微信内使用，可以使用网页授权方式。

### 修改 OAuth 服务

需要在 `oauth_service.py` 中添加判断：

```python
elif provider == OAuthProvider.WECHAT:
    # 判断是扫码登录还是微信内授权
    if user_agent_contains("MicroMessenger"):
        # 微信内网页授权
        auth_url = "https://open.weixin.qq.com/connect/oauth2/authorize"
        scope = "snsapi_userinfo"
    else:
        # PC 扫码登录
        auth_url = "https://open.weixin.qq.com/connect/qrconnect"
        scope = "snsapi_login"
```

### 创建公众号应用

1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 注册公众号（服务号，需认证）
3. **接口权限** → **网页授权** → **修改**
4. 设置授权回调域名

**注意**：网页授权只支持微信客户端内使用，不支持 PC 扫码。

## 调试技巧

### 查看实际生成的 redirect_uri

在 `backend/app/services/oauth_service.py` 中添加日志：

```python
def get_authorization_url(self, provider: str, redirect_uri: str, state: str) -> str:
    print(f"[DEBUG] {provider} redirect_uri: {redirect_uri}")
    # ...
```

### 使用微信开发者工具

微信开发者工具可以模拟微信内环境：
1. 下载 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 创建网页调试项目
3. 在微信内环境调试网页授权

## 测试号方案（仅开发测试）

如果没有企业资质，可以使用微信测试号进行开发测试：

1. 访问 [微信公众平台测试号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
2. 扫码登录
3. 获取测试号信息：
   - appID
   - appsecret
4. 配置 **授权回调域名**（可以是内网穿透域名）

**限制**：
- 只能在微信客户端内测试
- 不支持 PC 扫码登录
- 无法正式上线
