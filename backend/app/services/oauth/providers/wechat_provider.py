"""
微信 OAuth Provider 实现
"""
from urllib.parse import quote

from app.services.oauth.base import BaseOAuthProvider, OAuthUserInfo


class WeChatProvider(BaseOAuthProvider):
    """微信 OAuth Provider"""

    def __init__(self, config):
        super().__init__(config)
        # 微信特殊：需要保存 openid 用于获取用户信息
        self._openid = None

    @property
    def provider_name(self) -> str:
        return "wechat"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        # 微信使用 appid 而不是 client_id
        # redirect_uri 必须进行 URL 编码
        encoded_redirect_uri = quote(redirect_uri, safe='')
        return (
            f"{self.config.auth_url}"
            f"?appid={self.config.client_id}"
            f"&redirect_uri={encoded_redirect_uri}"
            f"&response_type=code"
            f"&scope={self.config.scope}"
            f"&state={state}#wechat_redirect"
        )

    async def get_access_token(self, code: str, redirect_uri: str, client) -> str:
        # 微信使用 GET 请求获取 access_token
        token_response = await client.get(
            self.config.token_url,
            params={
                "appid": self.config.client_id,
                "secret": self.config.client_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_response.json()

        if "errcode" in token_data and token_data["errcode"] != 0:
            raise ValueError(token_data.get("errmsg", "Failed to get access token"))

        # 保存 openid 供后续使用
        self._openid = token_data.get("openid")
        return token_data["access_token"]

    async def get_user_info(self, access_token: str, client) -> OAuthUserInfo:
        # 微信需要使用 openid 获取用户信息
        if not self._openid:
            raise ValueError(
                "微信登录失败：未获取到 openid，请重新授权。"
                "这通常发生在 access_token 和 get_user_info 分别调用的情况下。"
            )

        # 获取用户信息
        user_response = await client.get(
            self.config.user_url,
            params={"access_token": access_token, "openid": self._openid},
        )
        user_data = user_response.json()

        if "errcode" in user_data and user_data["errcode"] != 0:
            raise ValueError(user_data.get("errmsg", "Failed to get user info"))

        # 使用 unionid（如果有）或 openid 作为用户 ID
        provider_user_id = user_data.get("unionid") or self._openid

        return OAuthUserInfo(
            provider_user_id=provider_user_id,
            email=None,  # 微信不提供邮箱
            name=user_data.get("nickname", "微信用户"),
            avatar_url=user_data.get("headimgurl"),
            phone=user_data.get("phone") or user_data.get("mobile"),
        )
