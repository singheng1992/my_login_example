from httpx import AsyncClient
from urllib.parse import parse_qs, urlparse


class TestOAuth:
    """OAuth 登录测试"""

    async def test_github_oauth_get_auth_url(self, client: AsyncClient):
        """测试获取 GitHub OAuth 授权 URL"""
        response = await client.get("/api/auth/oauth/github")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data["data"]
        assert "state" in data["data"]

        # 验证 state 是 32 位随机字符串
        state = data["data"]["state"]
        assert len(state) == 32
        assert state.isalnum()

        # 验证 auth_url 包含必要的参数
        auth_url = data["data"]["auth_url"]
        assert "github.com/login/oauth/authorize" in auth_url
        assert "client_id=" in auth_url
        assert "redirect_uri=" in auth_url
        assert "state=" in auth_url
        assert f"state={state}" in auth_url

    async def test_oauth_callback_missing_code(self, client: AsyncClient):
        """测试回调缺少 code 参数 - 应重定向到前端并显示错误"""
        response = await client.get("/api/auth/oauth/github/callback", follow_redirects=False)
        assert response.status_code == 302
        # 验证重定向到前端
        assert "localhost:8080" in response.headers.get("location", "")

    async def test_oauth_callback_invalid_state(self, client: AsyncClient):
        """测试回调使用无效 state - 应重定向到前端并显示错误"""
        response = await client.get(
            "/api/auth/oauth/github/callback?code=test_code&state=invalid_state",
            follow_redirects=False
        )
        assert response.status_code == 302
        # 验证重定向到前端并包含错误信息
        location = response.headers.get("location", "")
        assert "localhost:8080" in location
        assert "error=" in location

    async def test_github_oauth_state_uniqueness(self, client: AsyncClient):
        """测试每次生成的 state 都不同"""
        responses = []
        for _ in range(5):
            response = await client.get("/api/auth/oauth/github")
            state = response.json()["data"]["state"]
            responses.append(state)

        # 验证所有 state 都不同
        assert len(set(responses)) == 5

    async def test_google_oauth_unsupported(self, client: AsyncClient):
        """测试不支持的 OAuth 提供商"""
        response = await client.get("/api/auth/oauth/unsupported")
        assert response.status_code == 400
