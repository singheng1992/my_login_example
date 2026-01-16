# 微信公众平台服务器配置指南

## 功能说明

微信公众平台服务器配置用于接收微信推送的消息和事件，例如：
- 用户关注/取消关注事件
- 用户发送的文本、图片等消息
- 自定义菜单点击事件
- 扫码事件

**注意：** 这与 OAuth 扫码登录是不同的功能。

| 功能 | 用途 | 接口 URL |
|------|------|----------|
| **OAuth 扫码登录** | 用户扫码登录网站 | `/api/auth/oauth/wechat` |
| **服务器配置** | 接收微信推送消息 | `/api/auth/wechat/mp/server` |

## 前置条件

1. **微信公众平台账号**
   - 访问 [微信公众平台](https://mp.weixin.qq.com/)
   - 注册公众号（订阅号或服务号）
   - 或使用 [测试号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login) 进行开发测试

2. **服务器要求**
   - 公网可访问的服务器（或内网穿透工具，如 ngrok）
   - 支持 80 端口（HTTP）或 443 端口（HTTPS）
   - 微信服务器需要在 5 秒内收到响应

## 配置步骤

### 步骤 1: 获取测试号（推荐用于开发）

1. 访问 [微信公众平台测试号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
2. 使用微信扫描登录
3. 获取以下信息：
   - **appID**：测试号微信号
   - **appsecret**：测试号密钥

### 步骤 2: 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# 微信公众平台配置（用于接收推送消息）
WECHAT_MP_TOKEN=your_token_here
WECHAT_MP_ENCODING_AES_KEY=
```

**参数说明：**
- `WECHAT_MP_TOKEN`：自定义的 Token（3-32 个字符），用于验证服务器
- `WECHAT_MP_ENCODING_AES_KEY`：消息加密密钥（可选，安全模式需要）

**Token 示例：**
```bash
WECHAT_MP_TOKEN=my_login_demo_token_2024
```

### 步骤 3: 配置服务器地址

在微信公众平台测试号页面：

**接口配置信息：**
- **URL**：`https://yourdomain.com/api/auth/wechat/mp/server`
- **Token**：与 `.env` 中的 `WECHAT_MP_TOKEN` 保持一致

**注意事项：**
1. URL 必须是 80 或 443 端口
2. URL 必须是公网可访问的
3. Token 必须与后端配置一致

### 步骤 4: 点击提交

微信服务器会向配置的 URL 发送 GET 请求进行验证：

```
GET https://yourdomain.com/api/auth/wechat/mp/server?signature=xxx&timestamp=xxx&nonce=xxx&echostr=xxx
```

验证成功后，会显示 "提交成功"。

## 本地开发调试

使用内网穿透工具暴露本地服务：

### 使用 ngrok

```bash
# 安装 ngrok
brew install ngrok

# 启动后端服务
cd backend
uvicorn app.main:app --reload --port 8000

# 新终端窗口启动 ngrok
ngrok http 8000
```

ngrok 会生成一个公网 URL，例如：`https://abc123.ngrok.io`

然后在微信公众平台配置：
- **URL**：`https://abc123.ngrok.io/api/auth/wechat/mp/server`

### 使用 localtunnel

```bash
# 安装 localtunnel
npm install -g localtunnel

# 启动后端服务
cd backend
uvicorn app.main:app --reload --port 8000

# 新终端窗口启动 localtunnel
lt --port 8000
```

## API 接口说明

### GET /api/auth/wechat/mp/server

微信服务器验证接口。

**请求参数：**
| 参数 | 描述 |
|------|------|
| signature | 微信加密签名 |
| timestamp | 时间戳 |
| nonce | 随机数 |
| echostr | 随机字符串 |

**验证流程：**
1. 将 token、timestamp、nonce 三个参数进行字典序排序
2. 将三个参数字符串拼接成一个字符串进行 sha1 加密
3. 加密后的字符串与 signature 对比

**响应：**
- 成功：返回 echostr 原值
- 失败：返回 403

### POST /api/auth/wechat/mp/server

接收微信推送消息接口。

**请求体：** XML 格式

**消息类型：**
- `event`：事件（关注/取消关注、菜单点击等）
- `text`：文本消息
- `image`：图片消息
- `voice`：语音消息
- `video`：视频消息
- `location`：位置消息
- `link`：链接消息

**事件类型：**
- `subscribe`：用户关注
- `unsubscribe`：用户取消关注
- `CLICK`：菜单点击
- `SCAN`：扫码

## 消息格式示例

### 关注事件

```xml
<xml>
  <ToUserName><![CDATA[公众号ID]]></ToUserName>
  <FromUserName><![CDATA[用户OpenID]]></FromUserName>
  <CreateTime>1234567890</CreateTime>
  <MsgType><![CDATA[event]]></MsgType>
  <Event><![CDATA[subscribe]]></Event>
</xml>
```

### 文本消息

```xml
<xml>
  <ToUserName><![CDATA[公众号ID]]></ToUserName>
  <FromUserName><![CDATA[用户OpenID]]></FromUserName>
  <CreateTime>1234567890</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[你好]]></Content>
  <MsgId>1234567890123456</MsgId>
</xml>
```

### 菜单点击事件

```xml
<xml>
  <ToUserName><![CDATA[公众号ID]]></ToUserName>
  <FromUserName><![CDATA[用户OpenID]]></FromUserName>
  <CreateTime>1234567890</CreateTime>
  <MsgType><![CDATA[event]]></MsgType>
  <Event><![CDATA[CLICK]]></Event>
  <EventKey><![CDATA[菜单键值]]></EventKey>
</xml>
```

## 扩展功能

### 解析 XML 消息

安装 `xmltodict` 库：

```bash
uv add xmltodict
```

在 `wechat_mp_server_message` 中解析：

```python
import xmltodict

async def wechat_mp_server_message(request: Request):
    body = await request.body()
    data = xmltodict.parse(body.decode('utf-8'))

    msg_type = data['xml']['MsgType']
    from_user = data['xml']['FromUserName']
    to_user = data['xml']['ToUserName']

    if msg_type == 'event':
        event = data['xml']['Event']
        if event == 'subscribe':
            # 用户关注事件
            print(f"用户 {from_user} 关注了公众号")
        elif event == 'unsubscribe':
            # 用户取消关注事件
            print(f"用户 {from_user} 取消关注")
    elif msg_type == 'text':
        content = data['xml']['Content']
        # 处理文本消息
        print(f"用户 {from_user} 发送: {content}")

    return Response(content="", media_type="text/plain")
```

### 自动回复消息

回复文本消息示例：

```python
def create_text_message(to_user: str, from_user: str, content: str) -> str:
    """创建文本消息 XML"""
    return f"""<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>1234567890</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
</xml>"""

async def wechat_mp_server_message(request: Request):
    body = await request.body()
    data = xmltodict.parse(body.decode('utf-8'))

    from_user = data['xml']['FromUserName']  # 用户 OpenID
    to_user = data['xml']['ToUserName']      # 公众号 ID
    msg_type = data['xml']['MsgType']

    if msg_type == 'text':
        content = data['xml']['Content']
        # 自动回复
        reply = create_text_message(from_user, to_user, f"你发送了: {content}")
        return Response(content=reply, media_type="application/xml")

    return Response(content="", media_type="text/plain")
```

## 生产环境配置

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用 HTTPS（推荐）

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见问题

### 1. 验证失败

**可能原因：**
- Token 配置不一致
- URL 无法访问
- 服务器响应超时

**解决方法：**
1. 检查 `.env` 中的 `WECHAT_MP_TOKEN` 是否与公众平台配置一致
2. 确认服务器可以通过公网访问
3. 查看后端日志，确认收到请求

### 2. URL 包含无效参数

**可能原因：**
- URL 路径错误
- 使用了非 80/443 端口

**解决方法：**
1. 确认 URL 格式：`https://yourdomain.com/api/auth/wechat/mp/server`
2. 使用标准端口（80 或 443）

### 3. 消息推送失败

**可能原因：**
- 服务器响应超过 5 秒
- 返回格式错误

**解决方法：**
1. 优化业务逻辑，确保快速响应
2. 使用异步任务处理复杂逻辑
3. 返回空字符串表示不回复

## 调试技巧

### 查看后端日志

```bash
# 启动后端时会打印验证日志
[微信服务器验证] 成功: timestamp=1234567890, nonce=abc123

# 收到消息时会打印消息内容
[微信推送消息] 收到消息: <xml>...
```

### 使用微信开发者工具

1. 下载 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 创建公众号调试项目
3. 模拟消息推送

### 使用微信公众平台调试工具

微信公众平台提供了 URL 验证工具，可以测试接口是否正常。

## 相关链接

- [微信公众平台接入概述](https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Access_Overview.html)
- [微信公众平台测试号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
- [微信消息接口指南](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_message_standard.html)
