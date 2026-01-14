from httpx import AsyncClient
import uuid


class TestSessions:
    """Session 管理接口测试"""

    async def test_login_creates_session(self, client: AsyncClient):
        """测试登录后创建 session 记录"""
        # 使用唯一的用户名
        unique_id = str(uuid.uuid4())[:8]

        # 注册用户
        await client.post(
            "/api/auth/register",
            json={
                "username": f"sessionuser_{unique_id}",
                "password": "password123",
                "nickname": "Session用户"
            }
        )

        # 登录
        response = await client.post(
            "/api/auth/login/password",
            json={
                "username": f"sessionuser_{unique_id}",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        token = data["data"]["access_token"]

        # 获取 sessions 列表
        sessions_response = await client.get(
            "/api/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert sessions_response.status_code == 200
        sessions = sessions_response.json()["data"]
        # 注册和登录各创建一个 session，所以应该是 2 个
        assert len(sessions) >= 1
        assert "device_info" in sessions[0]
        assert "created_at" in sessions[0]

    async def test_logout_revokes_session(self, client: AsyncClient):
        """测试登出后 session 被撤销"""
        # 使用唯一的用户名
        unique_id = str(uuid.uuid4())[:8]

        # 注册用户
        await client.post(
            "/api/auth/register",
            json={
                "username": f"logoutuser_{unique_id}",
                "password": "password123",
                "nickname": "登出用户"
            }
        )

        # 登录
        login_response = await client.post(
            "/api/auth/login/password",
            json={
                "username": f"logoutuser_{unique_id}",
                "password": "password123"
            }
        )
        token = login_response.json()["data"]["access_token"]

        # 登出
        logout_response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_response.status_code == 200

        # 使用已登出的 token 访问受保护接口应该失败
        protected_response = await client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 401
        assert "revoked" in protected_response.json()["detail"].lower()

    async def test_revoke_session(self, client: AsyncClient):
        """测试撤销指定 session"""
        # 使用唯一的用户名
        unique_id = str(uuid.uuid4())[:8]

        # 注册用户
        await client.post(
            "/api/auth/register",
            json={
                "username": f"revokeuser_{unique_id}",
                "password": "password123",
                "nickname": "撤销用户"
            }
        )

        # 登录
        login_response = await client.post(
            "/api/auth/login/password",
            json={
                "username": f"revokeuser_{unique_id}",
                "password": "password123"
            }
        )
        token = login_response.json()["data"]["access_token"]

        # 获取 sessions 列表
        sessions_response = await client.get(
            "/api/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        sessions = sessions_response.json()["data"]
        session_id = sessions[0]["id"]

        # 撤销 session
        revoke_response = await client.post(
            f"/api/sessions/{session_id}/revoke",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert revoke_response.status_code == 200

        # 使用被撤销的 token 访问应该失败
        protected_response = await client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 401

