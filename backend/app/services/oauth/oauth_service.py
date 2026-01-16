"""
OAuth 服务（重构后）

使用工厂模式管理 OAuth Provider，每个 Provider 独立实现。
"""

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oauth_account import OAuthAccount
from app.models.user import User
from app.services.oauth.factory import OAuthProviderFactory


class OAuthProvider:
    """OAuth Provider 常量"""

    GITHUB = "github"
    GOOGLE = "google"
    WECHAT = "wechat"
    DINGTALK = "dingtalk"
    FEISHU = "feishu"


class OAuthService:
    """OAuth 服务（重构后）

    使用工厂模式管理 OAuth Provider，添加新 Provider 不需要修改此类。
    """

    def __init__(self):
        # 不再需要 self.providers 字典配置
        pass

    def get_authorization_url(
        self, provider: str, redirect_uri: str, state: str
    ) -> str:
        """获取授权 URL

        Args:
            provider: Provider 名称
            redirect_uri: 回调地址
            state: 防CSRF攻击的随机字符串

        Returns:
            授权 URL

        Raises:
            ValueError: 不支持的 provider
        """
        provider_instance = OAuthProviderFactory.create(provider)
        return provider_instance.get_authorization_url(redirect_uri, state)

    async def get_user_info(self, provider: str, code: str, redirect_uri: str) -> dict:
        """获取用户信息

        Args:
            provider: Provider 名称
            code: 授权码
            redirect_uri: 回调地址

        Returns:
            标准化用户信息字典，包含：
            - provider_user_id: Provider 用户 ID
            - email: 邮箱（可能为 None）
            - name: 姓名
            - avatar_url: 头像 URL（可能为 None）

        Raises:
            ValueError: 获取失败时抛出异常
        """
        provider_instance = OAuthProviderFactory.create(provider)

        async with httpx.AsyncClient() as client:
            # 获取 access token（微信会同时保存 openid）
            access_token = await provider_instance.get_access_token(
                code, redirect_uri, client
            )
            # 获取用户信息
            user_info = await provider_instance.get_user_info(access_token, client)
            return {
                "provider_user_id": user_info.provider_user_id,
                "email": user_info.email,
                "name": user_info.name,
                "avatar_url": user_info.avatar_url,
                "phone": user_info.phone,
            }

    async def find_or_create_user(
        self, provider: str, provider_user_id: str, user_info: dict, db: AsyncSession
    ) -> User:
        """查找或创建用户

        注意：不从第三方平台获取用户信息填充到 users 表。
        新创建的用户需要手动补充 email、phone、nickname、avatar_url 等信息。

        Args:
            provider: Provider 名称
            provider_user_id: Provider 用户 ID
            user_info: 用户信息字典（不用于填充用户数据）
            db: 数据库会话

        Returns:
            用户实例
        """
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
                OAuthAccount.is_deleted == False,
            )
        )
        oauth_account = result.scalar_one_or_none()

        if oauth_account:
            user_result = await db.execute(
                select(User).where(
                    User.id == oauth_account.user_id, User.is_deleted == False
                )
            )
            return user_result.scalar_one()

        # 创建新用户，不使用第三方平台的用户信息
        # 使用默认昵称，用户后续需要补充个人信息
        provider_names = {
            "github": "GitHub用户",
            "google": "Google用户",
            "wechat": "微信用户",
            "dingtalk": "钉钉用户",
            "feishu": "飞书用户",
        }
        default_nickname = provider_names.get(provider, "OAuth用户")

        user = User(
            nickname=default_nickname,
            email=None,  # 不自动填充
            avatar_url=None,  # 不自动填充
            phone=None,  # 不自动填充
        )
        db.add(user)
        await db.flush()

        oauth_account = OAuthAccount(
            user_id=user.id, provider=provider, provider_user_id=provider_user_id
        )
        db.add(oauth_account)
        await db.commit()

        return user


# 全局单例
oauth_service = OAuthService()
