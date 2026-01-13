# 登录系统设计方案

**日期**: 2025-01-13
**类型**: 可用的Demo系统

## 一、项目概述

实现一个前后端分离的登录演示项目，支持多种登录方式。

### 登录方式
- 账号密码登录
- 邮箱验证码登录
- 手机验证码登录
- 第三方登录（GitHub、Google、微信、钉钉、飞书）

### 技术栈
- **后端**: Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy, Redis, JWT
- **前端**: HTML5, CSS3, 原生JavaScript

## 二、系统架构

### 后端分层设计
- **API层**: 处理HTTP请求和响应，参数验证
- **业务逻辑层**: 处理登录、注册等核心业务逻辑
- **数据访问层**: SQLAlchemy异步ORM
- **外部服务层**: 邮件、短信、OAuth客户端

### 前端结构
- 多页面设计：login.html、register.html、profile.html
- 静态资源在 `/static` 目录
- fetch API与后端通信

## 三、数据库设计

### users 表
```sql
- id (UUID, PK)
- username (varchar, unique, nullable)
- email (varchar, unique, nullable)
- phone (varchar, unique, nullable)
- password_hash (varchar, nullable)
- nickname (varchar)
- avatar_url (varchar, nullable)
- is_deleted (boolean, default false)
- created_at (timestamp)
- updated_at (timestamp)
```

### oauth_accounts 表
```sql
- id (UUID, PK)
- user_id (UUID)
- provider (varchar) -- github/google/wechat/dingtalk/feishu
- provider_user_id (varchar)
- access_token (text, nullable)
- refresh_token (text, nullable)
- is_deleted (boolean, default false)
- created_at (timestamp)
```

### verification_codes 表
```sql
- id (UUID, PK)
- identifier (varchar) -- 邮箱或手机号
- code (varchar)
- type (varchar) -- email/sms
- expires_at (timestamp)
- used (boolean)
- is_deleted (boolean, default false)
```

## 四、登录流程

### 账号密码登录
1. 用户输入用户名/邮箱 + 密码
2. 后端验证用户存在且密码正确
3. 生成JWT Token返回

### 邮箱验证码登录
1. 用户输入邮箱，点击"发送验证码"
2. 后端通过SMTP发送6位验证码
3. 用户输入验证码，后端验证并生成Token

### 手机验证码登录
1. 类似邮箱验证码流程
2. 使用阿里云/腾讯云短信API

### 第三方登录（OAuth2）
1. 前端跳转到第三方授权页面
2. 用户授权后回调到后端
3. 后端用code换取access_token
4. 获取用户信息，匹配或创建账号
5. 返回JWT Token

### 安全措施
- 验证码5分钟有效期，只能使用一次
- 同一邮箱/手机60秒内只能发送一次
- 登录失败5次锁定账户30分钟
- JWT Token有效期7天

## 五、API接口

### 认证接口
```
POST /api/auth/register
POST /api/auth/login/password
POST /api/auth/login/email
POST /api/auth/login/sms
GET  /api/auth/oauth/{provider}
GET  /api/auth/oauth/{provider}/callback
POST /api/auth/logout
POST /api/auth/refresh
```

### 验证码接口
```
POST /api/auth/send-email
POST /api/auth/send-sms
```

### 用户接口
```
GET    /api/user/profile
PUT    /api/user/profile
POST   /api/user/avatar
```

### 响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": {...}
}
```

## 六、目录结构

```
my_login_example/
├── backend/
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 配置、安全、JWT
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic模式
│   │   ├── services/      # 业务逻辑
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── start.sh           # 后端启动脚本
├── frontend/
│   ├── static/
│   ├── templates/
│   ├── config.js
│   └── start.sh           # 前端启动脚本
├── docker-compose.yml     # PostgreSQL + Redis
└── README.md
```

## 七、核心配置

### 环境变量（.env）
- 数据库连接
- Redis连接
- JWT密钥
- SMTP配置
- 短信API配置
- OAuth应用配置

### 启动方式
- 后端: `cd backend && ./start.sh`
- 前端: `cd frontend && ./start.sh`
- 数据库: `docker-compose up -d`
