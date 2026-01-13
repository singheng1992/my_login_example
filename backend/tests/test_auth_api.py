from httpx import AsyncClient


class TestRegister:
    """注册接口测试"""

    async def test_register_success(self, client: AsyncClient):
        """测试成功注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "testpass123",
                "nickname": "测试用户",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert data["data"]["user"]["username"] == "testuser"

    async def test_register_duplicate_username(self, client: AsyncClient):
        """测试重复用户名注册"""
        # 第一次注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "password": "testpass123",
                "nickname": "用户1"
            }
        )

        # 第二次注册相同用户名
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "password": "testpass123",
                "nickname": "用户2"
            }
        )
        assert response.status_code == 400

    async def test_register_invalid_email(self, client: AsyncClient):
        """测试无效邮箱格式"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser2",
                "password": "testpass123",
                "nickname": "测试",
                "email": "invalid-email"
            }
        )
        assert response.status_code == 422  # 验证错误


class TestPasswordLogin:
    """密码登录测试"""

    async def test_login_success(self, client: AsyncClient):
        """测试登录成功"""
        # 先注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "loginuser",
                "password": "password123",
                "nickname": "登录用户"
            }
        )

        # 登录
        response = await client.post(
            "/api/auth/login/password",
            json={
                "username": "loginuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]

    async def test_login_wrong_password(self, client: AsyncClient):
        """测试错误密码登录"""
        response = await client.post(
            "/api/auth/login/password",
            json={
                "username": "loginuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在用户登录"""
        response = await client.post(
            "/api/auth/login/password",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401


class TestEmailLogin:
    """邮箱登录测试"""

    async def test_send_email_code(self, client: AsyncClient):
        """测试发送邮箱验证码"""
        response = await client.post(
            "/api/auth/send-email",
            json={
                "identifier": "test@example.com"
            }
        )
        # 由于没有配置SMTP，这里会失败，但测试API端点存在
        assert response.status_code in [200, 400]  # 取决于SMTP配置


class TestOAuth:
    """OAuth第三方登录测试"""

    async def test_oauth_github_url(self, client: AsyncClient):
        """测试获取GitHub授权URL"""
        response = await client.get("/api/auth/oauth/github")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data["data"]

    async def test_oauth_wechat_url(self, client: AsyncClient):
        """测试获取微信授权URL"""
        response = await client.get("/api/auth/oauth/wechat")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data["data"]

    async def test_oauth_unsupported_provider(self, client: AsyncClient):
        """测试不支持的OAuth提供商"""
        response = await client.get("/api/auth/oauth/unsupported")
        assert response.status_code == 400


class TestLogout:
    """登出测试"""

    async def test_logout(self, client: AsyncClient):
        """测试登出接口"""
        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
