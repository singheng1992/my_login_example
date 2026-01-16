"""
GitHub OAuth Provider 实现
"""

from app.services.oauth.base import BaseOAuthProvider, OAuthUserInfo


class GitHubProvider(BaseOAuthProvider):
    """GitHub OAuth Provider"""

    @property
    def provider_name(self) -> str:
        return "github"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        authorization_url = (
            f"{self.config.auth_url}"
            f"?client_id={self.config.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={self.config.scope}"
            f"&state={state}"
        )
        # print(f"authorization_url: {authorization_url}")
        return authorization_url

    async def get_access_token(self, code: str, redirect_uri: str, client) -> str:
        token_response = await client.post(
            self.config.token_url,
            data={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_response.json()
        # print(f"token_data: {token_data}")
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
        # print(f"user_data: {user_data}")

        # 如果 /user 返回的 email 为空，尝试从 /user/emails 获取
        email = user_data.get("email")
        if not email:
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails_data = emails_response.json()
            # 找到主邮箱（primary=true 且 verified=true）
            if isinstance(emails_data, list):
                for item in emails_data:
                    if item.get("primary") and item.get("verified"):
                        email = item.get("email")
                        break

        return OAuthUserInfo(
            provider_user_id=str(user_data["id"]),
            email=email,
            name=user_data.get("name") or user_data.get("login") or "GitHub用户",
            avatar_url=user_data.get("avatar_url"),
            phone=user_data.get("phone"),
        )
