# 钉钉 OAuth 登录配置指南

钉钉（DingTalk）是阿里巴巴推出的企业协作平台，提供 OAuth2.0 登录功能。

## 前置条件

1. 拥有钉钉开发者账号
2. 创建钉钉企业内部应用
3. 需要企业管理员权限

## 步骤 1: 创建钉钉开放平台应用

### 1.1 注册/登录钉钉开发者平台

1. 访问 [钉钉开发者平台](https://open-dev.dingtalk.com/)
2. 使用钉钉账号登录

### 1.2 创建企业内部应用

1. 进入 **应用开发** → **企业内部开发** → **H5微应用**
2. 点击 **创建应用**
3. 填写应用信息：
   - **应用名称**：`Login Demo`
   - **应用描述**：登录演示应用
   - **应用图标**：上传应用图标

### 1.3 获取凭证

创建成功后，进入应用详情页：
- **AppKey**：应用唯一标识（也叫 Client ID）
- **AppSecret**：应用密钥

**重要**：AppKey 和 AppSecret 需要保密，不要提交到代码仓库。

## 步骤 2: 配置 OAuth 权限

### 2.1 开启登录能力

1. 进入应用详情页
2. 点击左侧菜单 **登录与分享**
3. 开启 **钉钉扫码登录** 或 **钉钉账号密码登录**

### 2.2 配置回调地址

1. 在 **登录与分享** 页面，找到 **回调域名** 配置
2. 添加回调 URL：
   ```
   http://localhost:8000/api/auth/oauth/dingtalk/callback
   ```
3. 点击 **保存**

**注意**：
- 开发环境可以使用 `http://localhost`
- 生产环境必须使用 `https://`
- URL 必须完全匹配

### 2.3 配置应用权限

1. 点击左侧菜单 **权限管理**
2. 搜索并开通以下权限：
   - **获取成员信息**：`contact:user.base:readonly`
   - **获取用户邮箱**：`contact:user.email:readonly`
   - **获取用户手机号**：`contact:user.phone:readonly`（可选）

### 2.4 发布应用

1. 点击右上角 **版本管理** → **发布版本**
2. 选择发布版本
3. 填写版本说明
4. 点击 **确认发布**

## 步骤 3: 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# 钉钉 OAuth
OAUTH_DINGTALK_APP_ID=dingxxxxxxxxxxxxxxxx
OAUTH_DINGTALK_APP_SECRET=your_app_secret
```

## 步骤 4: 确保 SERVER_BASE_URL 正确配置

```bash
SERVER_BASE_URL=http://localhost:8000  # 开发环境
# SERVER_BASE_URL=https://api.yourdomain.com  # 生产环境
```

## 生产环境配置

### 钉钉开发者平台配置

**回调地址**：
```
https://api.yourdomain.com/api/auth/oauth/dingtalk/callback
```

### 环境变量配置

```bash
SERVER_BASE_URL=https://api.yourdomain.com
OAUTH_DINGTALK_APP_ID=dingxxxxxxxxxxxxxxxx
OAUTH_DINGTALK_APP_SECRET=production_app_secret
```

## 验证配置

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. 测试 OAuth 授权 URL

```bash
curl http://localhost:8000/api/auth/oauth/dingtalk
```

应该返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "auth_url": "https://login.dingtalk.com/oauth2/auth?client_id=...",
    "state": "..."
  }
}
```

### 3. 检查 auth_url

从返回的 `auth_url` 中验证：
- `client_id` 参数存在
- `redirect_uri` 正确
- `scope=openid corpid`
- `state` 参数存在
- `prompt=consent` 参数存在

## 钉钉 OAuth 流程

```
用户点击钉钉登录
        ↓
跳转钉钉授权页面（扫码/账号密码登录）
        ↓
用户扫码或输入账号密码
        ↓
用户授权应用
        ↓
钉钉回调 code
        ↓
后端换取 access_token
        ↓
获取用户信息
        ↓
创建/查找用户 → 返回 token
```

## 钉钉 API 返回数据格式

### 获取 Access Token

**请求**：
```http
POST https://api.dingtalk.com/v1.0/oauth2/userAccessToken
Content-Type: application/json

{
  "clientId": "dingxxxxxxxxxxxxxxxx",
  "clientSecret": "your_app_secret",
  "code": "authorization_code_from_callback",
  "grantType": "authorization_code"
}
```

**响应**：
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "Bearer",
  "expireIn": 7200
}
```

### 获取用户信息

**请求**：
```http
GET https://api.dingtalk.com/v1.0/contact/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**：
```json
{
  "unionId": "PqDiXxxxxxxxxxxxxxxxxxxx",
  "openId": "PqDiXxxxxxxxxxxxxxxxxxxx",
  "userName": "张三",
  "nick": "小张",
  "avatarUrl": "https://avatar.dingtalk.cn/...",
  "email": "zhangsan@example.com",
  "mobile": "13800138000",
  "stateCode": "86",
  "orgEmail": "zhangsan@company.com"
}
```

## 钉钉与其他 OAuth 的区别

| 特性 | GitHub OAuth | 钉钉 OAuth |
|------|-------------|-----------|
| 授权 URL | `/login/oauth/authorize` | `/oauth2/auth` |
| Token URL | `/login/oauth/access_token` | `/v1.0/oauth2/userAccessToken` |
| User Info URL | `/api/github.com/user` | `/v1.0/contact/users/me` |
| Client ID 参数名 | `client_id` | `client_id` (JSON) |
| Token 请求方式 | POST (form-data) | POST (JSON) |
| 用户 ID | `id` | `unionId` 或 `openId` |
| 提供邮箱 | ✅ | ✅ (有限制) |
| 错误码方式 | HTTP 状态码 | `error` 字段 |

## 钉钉权限说明

| 权限 | 权限值 | 说明 | 是否必需 |
|------|--------|------|----------|
| 获取成员信息 | `contact:user.base:readonly` | 获取用户姓名、头像等 | 必需 |
| 获取用户邮箱 | `contact:user.email:readonly` | 获取用户邮箱地址 | 推荐 |
| 获取用户手机号 | `contact:user.phone:readonly` | 获取用户手机号 | 可选 |

### 权限申请步骤

1. 进入 **权限管理**
2. 在搜索框中搜索权限名称
3. 点击 **申请权限**
4. 填写申请理由：
   ```
   用于实现用户登录功能，需要获取用户基本信息进行身份验证。
   ```
5. 提交申请
6. 等待企业管理员审批

## 钉钉登录的特殊说明

### unionId vs openId

钉钉提供两种用户标识：
- **unionId**：跨应用的用户唯一标识（推荐使用）
- **openId**：应用内的用户唯一标识

**建议**：使用 `unionId` 作为用户的唯一标识，这样可以跨应用识别用户。

### 企业内部应用 vs 第三方企业应用

### 企业内部应用

- 适用于企业内部使用
- 只能在创建应用的企业内使用
- 无需审核，开发完成即可使用
- 推荐用于企业内部系统

### 第三方企业应用

- 可以上架到钉钉应用市场
- 供所有钉钉企业使用
- 需要提交审核
- 适用于 SaaS 产品

**本示例使用企业内部应用**。

## 常见问题

### 1: redirect_uri 不匹配

**问题**：钉钉提示 `redirect_uri 不匹配`

**解决**：
1. 检查钉钉开发者平台的 **回调域名** 配置
2. 确保回调 URL 完全匹配（包括协议、域名、端口、路径）
3. 确认 `.env` 中的 `SERVER_BASE_URL` 配置正确

### 2: 权限不足

**问题**：获取用户信息时提示 `权限不足`

**解决**：
1. 检查应用是否已开通所需权限
2. 确认权限已审批通过
3. 检查 scope 参数是否包含所需权限

### 3: code 无效

**问题**：获取 access_token 时提示 `code 无效`

**解决**：
- `code` 只能使用一次
- `code` 有效期为 5 分钟
- 确保 state 验证通过后再使用 code

### 4: 应用未发布

**问题**：OAuth 授权时提示应用不可用

**解决**：
1. 进入钉钉开发者平台
2. 点击 **版本管理** → **发布版本**
3. 选择发布版本并确认

### 5: 获取不到邮箱

**问题**：用户信息中邮箱字段为空

**解决**：
1. 确认已申请 `contact:user.email:readonly` 权限
2. 确认权限已审批通过
3. 部分用户可能未设置邮箱，需要做兼容处理

### 6: 跨域问题

**问题**：前端调用钉钉 API 时出现跨域错误

**解决**：
- 前端不应该直接调用钉钉 API
- 所有钉钉 API 调用都应该通过后端进行
- 后端需要配置 CORS 允许前端域名访问

## 调试技巧

### 查看实际生成的 redirect_uri

在 `backend/app/services/oauth_service.py` 中，钉钉的日志已经内置：

```python
print(f"[钉钉] Token 响应: {token_data}")
print(f"[钉钉] 用户信息响应: {user_data}")
```

### 使用钉钉开发者工具

钉钉提供了开发者工具可以调试应用：
1. 访问 [钉钉开发者平台](https://open-dev.dingtalk.com/)
2. 进入应用详情
3. 使用 **API 调试** 功能测试接口

### 查看钉钉 API 文档

钉钉 API 文档：https://open.dingtalk.com/document/

## 钉钉扫码登录组件

如果需要使用钉钉官方的扫码登录组件，可以引入以下 JS：

```html
<script src="https://g.alicdn.com/dingding/h5-dingtalk-login/0.21.0/ddlogin.js"></script>
<script>
  window.DTFrameLogin({
    id: 'login_container',
    width: 300,
    height: 300,
  }, {
    redirect_uri: encodeURIComponent('https://your-domain.com/api/auth/oauth/dingtalk/callback'),
    client_id: 'your_app_key',
    scope: 'openid corpid',
    response_type: 'code',
    state: 'STATE',
    prompt: 'consent',
  }, (loginResult) => {
    // 登录成功
    const { code, state } = loginResult;
    // 将 code 发送给后端
  }, (errorMsg) => {
    // 登录失败
    console.error(errorMsg);
  });
</script>
```

## 本地调试

钉钉 OAuth 需要公网回调地址，本地调试需要使用内网穿透工具：

### 推荐：ngrok

```bash
# 安装 ngrok
brew install ngrok

# 启动内网穿透
ngrok http 8000

# 会得到一个公网地址，如：https://xxx.ngrok.io
```

然后在钉钉开发者平台配置回调地址：
```
https://xxx.ngrok.io/api/auth/oauth/dingtalk/callback
```

## 测试环境

钉钉不提供专门的测试环境，但可以：
1. 创建测试企业
2. 在测试企业中创建测试应用
3. 使用测试账号进行调试

## 费用说明

钉钉开发者平台基础功能免费：
- 创建企业内部应用：免费
- OAuth 登录：免费
- API 调用：免费（有频率限制）

高级功能可能需要付费，请参考 [钉钉价格](https://www.dingtalk.com/pricing)。

## 参考文档

- [钉钉 OAuth2.0 鉴权](https://open.dingtalk.com/document/connection/oauth2-0-authentication)
- [钉钉获取用户信息](https://open.dingtalk.com/document/development/obtain-user-info)
- [钉钉扫码登录](https://open.dingtalk.com/document/dingstart/tutorial-obtaining-user-personal-information)
