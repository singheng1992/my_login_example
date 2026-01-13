import pytest
from httpx import AsyncClient


class TestUserProfile:
    """用户信息接口测试"""

    async def test_get_profile_without_token(self, client: AsyncClient):
        """测试未登录获取个人信息"""
        response = await client.get("/api/user/profile")
        assert response.status_code == 401  # 未授权

    async def test_update_profile(self, client: AsyncClient):
        """测试更新个人信息"""
        # 先注册并登录获取token
        register_resp = await client.post(
            "/api/auth/register",
            json={
                "username": "profileuser",
                "password": "testpass123",
                "nickname": "原昵称"
            }
        )
        token = register_resp.json()["data"]["access_token"]

        # 更新个人信息
        response = await client.put(
            "/api/user/profile",
            json={"nickname": "新昵称"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["nickname"] == "新昵称"

    async def test_get_profile_with_token(self, client: AsyncClient):
        """测试登录后获取个人信息"""
        # 先注册并登录获取token
        register_resp = await client.post(
            "/api/auth/register",
            json={
                "username": "getuser",
                "password": "testpass123",
                "nickname": "获取用户"
            }
        )
        token = register_resp.json()["data"]["access_token"]

        # 获取个人信息
        response = await client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["username"] == "getuser"

    async def test_update_profile_with_invalid_token(self, client: AsyncClient):
        """测试使用无效token更新个人信息"""
        response = await client.put(
            "/api/user/profile",
            json={"nickname": "新昵称"},
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
