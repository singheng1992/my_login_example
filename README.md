# 登录演示系统

一个前后端分离的登录演示项目，支持多种登录方式。

## 功能特性

- 账号密码登录
- 邮箱验证码登录
- 手机验证码登录
- 第三方登录（GitHub、Google、微信、钉钉、飞书、支付宝）
- 个人中心

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- PostgreSQL 15
- Redis
- SQLAlchemy
- JWT

### 前端
- HTML5
- CSS3
- 原生JavaScript

## 快速开始

### 1. 启动数据库服务

```bash
docker-compose up -d
```

### 2. 启动后端服务

```bash
cd backend
./start.sh
```

后端将运行在 http://localhost:8000

### 3. 启动前端服务

```bash
cd frontend
./start.sh
```

前端将运行在 http://localhost:8080

### 4. 访问应用

打开浏览器访问 http://localhost:8080

## 配置说明

复制 `backend/.env.example` 到 `backend/.env` 并修改配置：

- SMTP配置（邮箱验证码）
- 短信API配置（阿里云）
- OAuth应用配置（第三方登录）

## API文档

启动后端后访问 http://localhost:8000/docs 查看完整API文档。

## 开发说明

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 目录结构

```
my_login_example/
├── backend/           # 后端代码
├── frontend/          # 前端代码
├── docs/             # 文档
└── docker-compose.yml # 数据库服务
```

## License

MIT
