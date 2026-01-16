# 飞书 OAuth 登录配置指南

飞书（Lark）是字节跳动推出的企业协作平台，提供 OAuth 登录功能。

## 前置条件

1. 拥有飞书开放平台账号
2. 创建飞书企业自建应用
3. 需要企业管理员权限

## 步骤 1: 创建飞书开放平台应用

### 1.1 注册/登录飞书开放平台

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 使用飞书账号登录

### 1.2 创建企业自建应用

1. 进入 **开放平台** → **创建企业自建应用**
2. 选择要创建应用的企业（如果没有企业，需要先创建企业）
3. 填写应用信息：
   - **应用名称**：`Login Demo`
   - **应用描述**：登录演示应用
   - **应用图标**：上传应用图标

### 1.3 获取凭证

创建成功后，进入应用详情页：
- **App ID**：应用唯一标识
- **App Secret**：应用密钥

## 步骤 2: 配置 OAuth 权限

### 2.1 开启 OAuth 能力

1. 进入应用详情页
2. 点击左侧菜单 **权限管理** → **权限配置**
3. 搜索并开启以下权限：
   - **获取用户邮箱**：`email`
   - **获取用户基本信息**：`contact:user.base:readonly`
   - **获取用户统一 ID**：`contact:user.identity:readonly`

### 2.2 配置回调地址

1. 点击左侧菜单 **安全设置** → **重定向 URL**
2. 添加重定向 URL：
   ```
   http://localhost:8000/api/auth/oauth/feishu/callback
   ```
3. 点击 **保存**

**注意**：
- 开发环境可以使用 `http://localhost`
- 生产环境必须使用 `https://`
- URL 必须完全匹配

### 2.3 发布应用

1. 点击右上角 **发布** 按钮
2. 选择发布版本
3. 填写版本说明
4. 点击 **确认发布**

## 步骤 3: 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# 飞书 OAuth
OAUTH_FEISHU_APP_ID=cli_xxxxxxxxxxxxx
OAUTH_FEISHU_APP_SECRET=your_app_secret
```

## 步骤 4: 确保 SERVER_BASE_URL 正确配置

```bash
SERVER_BASE_URL=http://localhost:8000  # 开发环境
# SERVER_BASE_URL=https://api.yourdomain.com  # 生产环境
```

## 生产环境配置

### 飞书开放平台配置

**重定向 URL**：
```
https://api.yourdomain.com/api/auth/oauth/feishu/callback
```

### 环境变量配置

```bash
SERVER_BASE_URL=https://api.yourdomain.com
OAUTH_FEISHU_APP_ID=cli_xxxxxxxxxxxxx
OAUTH_FEISHU_APP_SECRET=production_app_secret
```

## 验证配置

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. 测试 OAuth 授权 URL

```bash
curl http://localhost:8000/api/auth/oauth/feishu
```

应该返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "auth_url": "https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=...",
    "state": "..."
  }
}
```

### 3. 检查 auth_url

从返回的 `auth_url` 中验证：
- `app_id` 参数存在
- `redirect_uri` 正确
- `scope=email` 或其他权限
- `state` 参数存在

## 飞书 OAuth 流程

```
用户点击飞书登录
        ↓
跳转飞书授权页面
        ↓
用户扫码/账号密码登录
        ↓
用户授权应用
        ↓
飞书回调 code
        ↓
后端换取 access_token
        ↓
获取用户信息
        ↓
创建/查找用户 → 返回 token
```

## 飞书 API 返回数据格式

### 获取 Access Token

**请求**：
```http
POST https://open.feishu.cn/open-apis/authen/v1/oidc/access_token
Content-Type: application/json

{
  "app_id": "cli_xxxxxxxxxxxxx",
  "app_secret": "your_app_secret",
  "grant_type": "authorization_code",
  "code": "authorization_code_from_callback"
}
```

**响应**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "access_token": "t-xxxxxxxxxxxxxxxxxxxxxxxx",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "r-xxxxxxxxxxxxxxxxxxxxxxxx"
  }
}
```

### 获取用户信息

**请求**：
```http
GET https://open.feishu.cn/open-apis/authen/v1/user_info
Authorization: Bearer t-xxxxxxxxxxxxxxxxxxxxxxxx
```

**响应**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "user_id": "ou_xxxxxxxxxxxxxxxxxxxx",
    "union_id": "on_xxxxxxxxxxxxxxxxxxxx",
    "name": "张三",
    "en_name": "San Zhang",
    "email": "zhangsan@example.com",
    "avatar_url": "https://avatar.feishucdn.com/...",
    "mobile": "+8613800138000",
    "tenant_key": "cli_xxxxxxxxxxxxx"
  }
}
```

## 飞书与其他 OAuth 的区别

| 特性 | GitHub OAuth | Google OAuth | 飞书 OAuth |
|------|-------------|--------------|-----------|
| 授权 URL | `/login/oauth/authorize` | `/o/oauth2/v2/auth` | `/authen/v1/authorize` |
| Token URL | `/login/oauth/access_token` | `/token` | `/authen/v1/oidc/access_token` |
| User Info URL | `/api.github.com/user` | `/oauth2/v2/userinfo` | `/authen/v1/user_info` |
| Client ID 参数名 | `client_id` | `client_id` | `app_id` |
| Token 请求方式 | POST (form-data) | POST (form-data) | POST (JSON) |
| 用户 ID | `id` | `id` | `union_id` 或 `user_id` |
| 提供邮箱 | ✅ | ✅ | ✅ |
| 错误码方式 | HTTP 状态码 | `error` 字段 | `code` 字段 (0=成功) |

## 飞书权限说明

| 权限 | 权限值 | 说明 | 是否必需 |
|------|--------|------|----------|
| 获取用户邮箱 | `email` | 获取用户邮箱地址 | 推荐 |
| 获取用户基本信息 | `contact:user.base:readonly` | 获取用户姓名、头像等 | 必需 |
| 获取用户统一 ID | `contact:user.identity:readonly` | 获取用户 union_id | 推荐 |

### 权限申请步骤

1. 进入 **权限管理** → **权限配置**
2. 在搜索框中搜索权限名称
3. 点击 **申请权限**
4. 填写申请理由：
   ```
   用于实现用户登录功能，需要获取用户邮箱和基本信息进行身份验证。
   ```
5. 提交申请
6. 等待企业管理员审批

## 常见问题

### 1: redirect_uri 不匹配

**问题**：飞书提示 `redirect_uri 不匹配`

**解决**：
1. 检查飞书开放平台的 **重定向 URL** 配置
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
1. 进入飞书开放平台
2. 点击 **发布** 按钮
3. 选择发布版本并确认

### 5: 企业未认证

**问题**：某些功能需要企业认证

**解决**：
- 个人开发者可以使用飞书（有限制）
- 企业认证需要营业执照等材料
- 访问 [飞书企业认证](https://www.feishu.cn/hc/zh-cn/category/5343164)

## 调试技巧

### 查看实际生成的 redirect_uri

在 `backend/app/services/oauth_service.py` 中添加日志：

```python
def get_authorization_url(self, provider: str, redirect_uri: str, state: str) -> str:
    print(f"[DEBUG] {provider} redirect_uri: {redirect_uri}")
    # ...
```

### 使用飞书开发者工具

飞书提供了开发者工具可以调试应用：
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 进入应用详情
3. 使用 **API 调试** 功能测试接口

### 查看飞书 API 文档

飞书 API 文档：https://open.feishu.cn/document/server-docs/authentication-management/access-token

## 飞书企业自建应用 vs 飞书商店应用

### 企业自建应用

- 适用于企业内部使用
- 只能在创建应用的企业内使用
- 无需审核，开发完成即可使用
- 推荐用于企业内部系统

### 飞书商店应用

- 可以上架到飞书应用商店
- 供所有飞书用户使用
- 需要提交审核
- 适用于 SaaS 产品

**本示例使用企业自建应用**。

## 飞书多租户说明

飞书支持多租户架构：
- `tenant_key`：租户唯一标识（企业 ID）
- `user_id`：用户在租户内的唯一 ID
- `union_id`：跨应用的用户唯一 ID

**建议**：使用 `union_id` 作为用户的唯一标识，这样即使用户切换企业也能保持账号一致。

## 测试环境

飞书不提供专门的测试环境，但可以：
1. 创建测试企业
2. 在测试企业中创建测试应用
3. 使用测试账号进行调试

## 费用说明

飞书开放平台基础功能免费：
- 创建企业自建应用：免费
- OAuth 登录：免费
- API 调用：免费（有频率限制）

高级功能可能需要付费，请参考 [飞书价格](https://www.feishu.cn/hc/zh-cn/topic/5343175)。
