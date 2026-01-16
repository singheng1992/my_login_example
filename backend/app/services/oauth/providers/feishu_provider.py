"""
飞书 OAuth Provider 实现
"""

from app.services.oauth.base import BaseOAuthProvider, OAuthUserInfo


class FeishuProvider(BaseOAuthProvider):
    """飞书 OAuth Provider"""

    @property
    def provider_name(self) -> str:
        return "feishu"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        # 飞书使用 app_id 而不是 client_id
        return (
            f"{self.config.auth_url}"
            f"?app_id={self.config.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={self.config.scope}"
            f"&state={state}"
        )

    async def get_access_token(self, code: str, redirect_uri: str, client) -> str:
        # 飞书使用 POST JSON 请求获取 access_token
        token_response = await client.post(
            self.config.token_url,
            json={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/json"},
        )
        token_data = token_response.json()

        # 打印调试信息
        # print(f"[飞书] Token 响应: {token_data}")

        # 检查响应中的 code 字段
        if token_data.get("code") != 0:
            error_msg = token_data.get("msg", "Failed to get access token")
            raise ValueError(f"飞书 API 错误: {error_msg}")

        # 适配两种响应格式
        # 格式1: {"code": 0, "data": {"access_token": "t-xxx"}}
        # 格式2: {"code": 0, "access_token": "eyJ..."}
        if "data" in token_data and "access_token" in token_data["data"]:
            return token_data["data"]["access_token"]
        elif "access_token" in token_data:
            return token_data["access_token"]
        else:
            raise ValueError(f"飞书 API 响应格式无法解析: {token_data}")

    async def get_user_info(self, access_token: str, client) -> OAuthUserInfo:
        # 获取用户信息
        user_response = await client.get(
            self.config.user_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_response.json()

        # 打印调试信息
        # print(f"[飞书] 用户信息响应: {user_data}")

        if user_data.get("code") != 0:
            error_msg = user_data.get("msg", "Failed to get user info")
            raise ValueError(f"飞书用户信息 API 错误: {error_msg}")

        # 适配两种响应格式
        if "data" in user_data:
            user_info = user_data["data"]
        else:
            user_info = user_data
        # print(f"[飞书] 用户信息: {user_info}")
        return OAuthUserInfo(
            provider_user_id=user_info.get("user_id")
            or user_info.get("union_id")
            or user_info.get("open_id"),
            email=user_info.get("email"),
            name=user_info.get("name") or user_info.get("en_name") or "飞书用户",
            avatar_url=user_info.get("avatar_url"),
            phone=user_info.get("mobile"),
        )
