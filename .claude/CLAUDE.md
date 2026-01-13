## 项目说明

实现一个前后端分离的登录演示项目，支持多种登录方式。

### 登录方式
- 账号密码登录 - 支持用户名登录
- 邮箱验证码登录 - 通过邮箱SMTP协议发送验证码
- 手机验证码登录 - 通过API发送短信验证码
- 微信登录 - OAuth2第三方登录
- 钉钉登录 - OAuth2第三方登录
- 飞书登录 - OAuth2第三方登录
- 支付宝登录 - OAuth2第三方登录
- Google登录 - OAuth2第三方登录
- GitHub登录 - OAuth2第三方登录

### 技术栈

使用Superpowers让Claude Code写出工程级代码

#### 后端

- uv包管理工具
- Python 3.11+
- FastAPI 0.128.0
- PostgreSQL 15.0+
- SQLAlchemy 2.0.45 (异步ORM)
- Alembic (数据库迁移)
- Redis (缓存和令牌黑名单)
- JWT (身份认证)

#### 前端

- HTML5
- CSS3
- 原生JavaScript

