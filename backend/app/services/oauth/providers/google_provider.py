"""
Google OAuth Provider 实现
"""

from app.services.oauth.base import BaseOAuthProvider, OAuthConfig, OAuthUserInfo


class GoogleProvider(BaseOAuthProvider):
    """Google OAuth Provider"""

    @property
    def provider_name(self) -> str:
        return "google"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        return (
            f"{self.config.auth_url}"
            f"?client_id={self.config.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={self.config.scope}"
            f"&response_type=code"
            f"&state={state}"
        )

    async def get_access_token(self, code: str, redirect_uri: str, client) -> str:
        token_response = await client.post(
            self.config.token_url,
            data={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )
        token_data = token_response.json()

        if "error" in token_data:
            raise ValueError(
                token_data.get("error_description", "Failed to get access token")
            )

        return token_data["access_token"]

    async def get_user_info(self, access_token: str, client) -> OAuthUserInfo:
        user_response = await client.get(
            self.config.user_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_response.json()

        return OAuthUserInfo(
            provider_user_id=user_data["id"],
            email=user_data.get("email"),
            name=user_data.get("name") or "Google用户",
            avatar_url=user_data.get("picture"),
            phone=user_data.get("phone"),
        )
