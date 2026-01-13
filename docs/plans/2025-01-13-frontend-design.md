# 前端设计方案

## 项目概述

实现一个前后端分离的登录演示项目的前端部分，采用单页应用架构，现代简约风格。

## 技术选型

- HTML5
- CSS3
- 原生JavaScript (ES6+)
- 纯静态文件，直接用浏览器打开

## 整体架构

采用单页应用（SPA）架构，所有代码在一个index.html中，通过JavaScript控制视图切换。

### 视图结构

1. **未登录视图** - 包含登录/注册表单和OAuth登录按钮
2. **登录后视图** - 显示用户基础信息
3. **加载/错误状态** - 统一的状态提示组件

### 文件结构

```
frontend/
├── index.html          # 主入口，包含HTML结构
├── css/
│   └── style.css      # 所有样式
├── js/
│   ├── config.js      # API配置和常量
│   ├── utils.js       # 工具函数（验证、存储、toast）
│   ├── auth.js        # 登录/注册逻辑
│   ├── user.js        # 用户中心逻辑
│   └── main.js        # 主入口和视图切换
└── assets/
    └── images/        # OAuth登录图标
```

### 认证机制

使用localStorage存储JWT token，所有API请求携带Authorization头。后端CORS配置已支持http://localhost:8080。

## UI设计

### 登录表单

**布局**：卡片式居中布局

**标签页导航**：
- 密码登录（默认）
- 邮箱验证码
- 手机验证码

**密码登录表单**：
- 用户名输入框（带图标）
- 密码输入框（带显示/隐藏切换）
- 记住我复选框
- 登录按钮

**验证码登录表单**：
- 邮箱/手机号输入框
- 验证码输入框 + 发送验证码按钮（60秒倒计时）
- 登录按钮

**OAuth登录区域**：
- GitHub、Google、微信、钉钉、飞书、支付宝
- 30x30px图标按钮，带hover效果

**注册链接**：没有账号？立即注册

### 注册表单

**必填字段**：
- 用户名（3-20字符，字母数字下划线）
- 密码（8-32字符，需包含字母和数字）
- 确认密码
- 邮箱（可选）
- 手机号（可选）
- 昵称（可选，2-20字符）

**交互**：
- 密码强度实时提示（弱/中/强）
- 确认密码实时比对
- 注册成功后自动登录

### 用户中心

**布局结构**：
- 顶部导航栏（左侧：应用名称，右侧：用户头像 + 退出按钮）
- 主内容区居中显示用户信息卡片

**用户信息卡片**：
- 头像（80x80px圆形）
- 昵称、用户名、邮箱、手机号、注册时间

## 视觉样式

### 配色方案

| 元素 | 颜色值 |
|------|--------|
| 主背景 | #f5f7fa |
| 卡片背景 | #ffffff |
| 主色调 | #4a90e2 |
| 成功色 | #52c41a |
| 错误色 | #f5222d |
| 文字主色 | #262626 |
| 文字次色 | #8c8c8c |
| 边框色 | #d9d9d9 |

### 组件样式

- 卡片：16px圆角，24px内边距，`box-shadow: 0 2px 8px rgba(0,0,0,0.1)`
- 输入框：4px圆角，32px高度，focus时蓝色边框
- 按钮：4px圆角，32px高度，蓝色背景
- 标签页：下划线样式，选中时蓝色线条

### 动画效果

- 视图切换：淡入淡出（300ms）
- 按钮hover：背景色过渡（200ms）
- 输入框focus：边框颜色过渡（200ms）

## Toast消息提示

### 功能

- 成功提示（绿色图标）
- 错误提示（红色图标）
- 加载提示（旋转图标）
- 自动消失（3秒）
- 手动关闭

### API

```javascript
toast.success('登录成功')
toast.error('用户名或密码错误')
toast.loading('正在登录...')
toast.hide()
```

## 数据流和API调用

### 认证流程

1. 登录成功后将`access_token`存入`localStorage`
2. API请求Header携带：`Authorization: Bearer {token}`
3. 退出时清除token

### API配置

```javascript
const API_BASE_URL = 'http://localhost:8000/api'
```

### 请求封装

```javascript
async function request(url, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || '请求失败')
  }

  return data
}
```

## 表单验证

### 验证规则

```javascript
const validators = {
  username: (val) => /^[a-zA-Z0-9_]{3,20}$/.test(val),
  password: (val) => /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,32}$/.test(val),
  email: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val),
  phone: (val) => /^1[3-9]\d{9}$/.test(val),
  code: (val) => /^\d{6}$/.test(val),
  nickname: (val) => /^.{2,20}$/.test(val)
}
```

### 验证时机

- `blur`事件：输入框失去焦点时验证
- `input`事件：清除错误状态
- 提交时：统一验证所有字段

## OAuth登录

### 提供商列表

```javascript
const OAUTH_PROVIDERS = [
  { id: 'github', name: 'GitHub', icon: 'github.svg' },
  { id: 'google', name: 'Google', icon: 'google.svg' },
  { id: 'wechat', name: '微信', icon: 'wechat.svg' },
  { id: 'dingtalk', name: '钉钉', icon: 'dingtalk.svg' },
  { id: 'feishu', name: '飞书', icon: 'feishu.svg' },
  { id: 'alipay', name: '支付宝', icon: 'alipay.svg' }
]
```

### 登录流程

1. 调用 `/api/auth/oauth/{provider}` 获取授权URL
2. 当前窗口跳转到授权URL
3. 授权后回调到 `/api/auth/oauth/{provider}/callback`
4. 后端返回token和用户信息
5. 保存token，切换到用户中心视图

## 验证码倒计时

### 功能

- 发送成功后按钮禁用
- 60秒倒计时显示
- 倒计时结束恢复按钮

### 实现

```javascript
let countdownTimer = null
let countdownSeconds = 60

function startCountdown(button) {
  button.disabled = true
  button.textContent = `${countdownSeconds}s后重发`

  countdownTimer = setInterval(() => {
    countdownSeconds--
    if (countdownSeconds <= 0) {
      clearInterval(countdownTimer)
      button.disabled = false
      button.textContent = '发送验证码'
      countdownSeconds = 60
    } else {
      button.textContent = `${countdownSeconds}s后重发`
    }
  }, 1000)
}
```

## 响应式设计

### 断点

- **移动端** (默认): 100%宽度
- **平板端** (768px+): 400px宽度
- **桌面端** (1024px+): 400px宽度

### 触摸优化

- 按钮最小点击区域：44x44px
- 移动端输入框字体：16px（防止iOS自动缩放）
- OAuth图标：移动端3列显示

## 安全性和最佳实践

- 所有用户输入使用`textContent`防止XSS
- 敏感信息不记录在console
- 表单提交时禁用按钮防止重复提交
- 网络请求超时设置（10秒）
- 使用`const`和`let`，避免`var`
- 关键操作添加注释说明
