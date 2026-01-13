import httpx
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.core.config import get_settings

settings = get_settings()


class OAuthProvider:
    GITHUB = "github"
    GOOGLE = "google"
    WECHAT = "wechat"
    DINGTALK = "dingtalk"
    FEISHU = "feishu"


class OAuthService:
    def __init__(self):
        self.providers = {
            OAuthProvider.GITHUB: {
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_url": "https://api.github.com/user",
                "client_id": settings.OAUTH_GITHUB_CLIENT_ID,
                "client_secret": settings.OAUTH_GITHUB_CLIENT_SECRET,
                "scope": "user:email"
            },
            OAuthProvider.GOOGLE: {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
                "scope": "openid email profile"
            }
        }

    def get_authorization_url(self, provider: str, redirect_uri: str, state: str) -> str:
        config = self.providers.get(provider)
        if not config:
            raise ValueError(f"Unsupported provider: {provider}")

        if provider == OAuthProvider.GITHUB:
            return f"{config['auth_url']}?client_id={config['client_id']}&redirect_uri={redirect_uri}&scope={config['scope']}&state={state}"
        elif provider == OAuthProvider.GOOGLE:
            return f"{config['auth_url']}?client_id={config['client_id']}&redirect_uri={redirect_uri}&scope={config['scope']}&response_type=code&state={state}"

        raise ValueError(f"Unsupported provider: {provider}")

    async def get_user_info(self, provider: str, code: str, redirect_uri: str) -> Dict:
        config = self.providers.get(provider)
        if not config:
            raise ValueError(f"Unsupported provider: {provider}")

        async with httpx.AsyncClient() as client:
            if provider == OAuthProvider.GITHUB:
                token_response = await client.post(
                    config["token_url"],
                    data={
                        "client_id": config["client_id"],
                        "client_secret": config["client_secret"],
                        "code": code
                    },
                    headers={"Accept": "application/json"}
                )
                token_data = token_response.json()

                if "error" in token_data:
                    raise ValueError(token_data.get("error_description", "Failed to get access token"))

                access_token = token_data["access_token"]

                user_response = await client.get(
                    config["user_url"],
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_data = user_response.json()

                return {
                    "provider_user_id": str(user_data["id"]),
                    "email": user_data.get("email"),
                    "name": user_data.get("name") or user_data.get("login"),
                    "avatar_url": user_data.get("avatar_url")
                }

            elif provider == OAuthProvider.GOOGLE:
                token_response = await client.post(
                    config["token_url"],
                    data={
                        "client_id": config["client_id"],
                        "client_secret": config["client_secret"],
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri
                    }
                )
                token_data = token_response.json()

                if "error" in token_data:
                    raise ValueError(token_data.get("error_description", "Failed to get access token"))

                access_token = token_data["access_token"]

                user_response = await client.get(
                    config["user_url"],
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_data = user_response.json()

                return {
                    "provider_user_id": user_data["id"],
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("picture")
                }

        raise ValueError(f"Unsupported provider: {provider}")

    async def find_or_create_user(self, provider: str, provider_user_id: str, user_info: Dict, db: AsyncSession) -> User:
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
                OAuthAccount.is_deleted == False
            )
        )
        oauth_account = result.scalar_one_or_none()

        if oauth_account:
            user_result = await db.execute(
                select(User).where(User.id == oauth_account.user_id, User.is_deleted == False)
            )
            return user_result.scalar_one()

        user = User(
            nickname=user_info.get("name", "Unknown"),
            email=user_info.get("email"),
            avatar_url=user_info.get("avatar_url")
        )
        db.add(user)
        await db.flush()

        oauth_account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id
        )
        db.add(oauth_account)
        await db.commit()

        return user


oauth_service = OAuthService()
