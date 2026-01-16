"""
钉钉 OAuth Provider 实现
"""

from app.services.oauth.base import BaseOAuthProvider, OAuthUserInfo


class DingTalkProvider(BaseOAuthProvider):
    """钉钉 OAuth Provider"""

    @property
    def provider_name(self) -> str:
        return "dingtalk"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        # 钉钉使用 client_id 和 prompt=consent
        return (
            f"{self.config.auth_url}"
            f"?client_id={self.config.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={self.config.scope}"
            f"&response_type=code"
            f"&state={state}"
            f"&prompt=consent"
        )

    async def get_access_token(self, code: str, redirect_uri: str, client) -> str:
        # 钉钉使用 POST JSON 请求获取 access_token
        token_response = await client.post(
            self.config.token_url,
            headers={"Content-Type": "application/json"},
            json={
                "clientId": self.config.client_id,  # 注意：驼峰命名
                "clientSecret": self.config.client_secret,  # 注意：驼峰命名
                "code": code,
                "refreshToken": "",  # 钉钉要求此字段，即使为空
                "grantType": "authorization_code",  # 注意：驼峰命名
            },
        )
        token_data = token_response.json()

        # 打印调试信息
        print(f"[钉钉] Token 响应: {token_data}")

        # 检查响应中的错误
        if "error" in token_data:
            error_msg = token_data.get(
                "error_description", "Failed to get access token"
            )
            raise ValueError(f"钉钉 API 错误: {error_msg}")

        # 钉钉返回格式: {"accessToken": "xxx", "expireIn": 7200}
        # 注意：accessToken 是驼峰命名
        access_token = token_data.get("accessToken")
        if not access_token:
            raise ValueError(f"钉钉 API 响应格式无法解析: {token_data}")

        return access_token

    async def get_user_info(self, access_token: str, client) -> OAuthUserInfo:
        # 获取用户信息
        # 钉钉使用自定义请求头 x-acs-dingtalk-access-token
        user_response = await client.get(
            self.config.user_url,
            headers={"x-acs-dingtalk-access-token": access_token},
        )
        user_data = user_response.json()

        # 打印调试信息
        print(f"[钉钉] 用户信息响应: {user_data}")

        # 钉钉可能返回错误格式
        if "errorCode" in user_data:
            error_msg = user_data.get("errorMsg", "Failed to get user info")
            raise ValueError(f"钉钉用户信息 API 错误: {error_msg}")

        # 钉钉返回格式可能有两种：
        # 格式1: {"unionId": "xxx", "userName": "xxx", "avatarUrl": "xxx"}
        # 格式2: {"code": 0, "data": {"unionId": "xxx", ...}}

        # 适配两种响应格式
        if "data" in user_data and isinstance(user_data["data"], dict):
            user_info = user_data["data"]
        else:
            user_info = user_data

        # 提取用户 ID：优先使用 unionId，其次 openId
        provider_user_id = (
            user_info.get("unionId")
            or user_info.get("openId")
            or user_info.get("union_id")  # 有时可能是下划线命名
            or user_info.get("open_id")
        )

        if not provider_user_id:
            raise ValueError(f"无法获取钉钉用户 ID，响应数据: {user_data}")

        return OAuthUserInfo(
            provider_user_id=str(provider_user_id),
            email=user_info.get("email"),
            name=user_info.get("userName")
            or user_info.get("nick")
            or user_info.get("name")
            or "钉钉用户",
            avatar_url=user_info.get("avatarUrl") or user_info.get("avatar_url"),
            phone=user_data.get("phone") or user_info.get("mobile"),
        )
