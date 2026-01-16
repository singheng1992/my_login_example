"""
OAuth Provider 工厂类

负责创建和管理 OAuth Provider 实例。
支持动态注册新的 Provider。
"""

from typing import Dict, Type

from app.core.config import get_settings
from app.services.oauth.base import BaseOAuthProvider, OAuthConfig

# 导入各个 Provider
from app.services.oauth.providers.dingtalk_provider import DingTalkProvider
from app.services.oauth.providers.feishu_provider import FeishuProvider
from app.services.oauth.providers.github_provider import GitHubProvider
from app.services.oauth.providers.google_provider import GoogleProvider
from app.services.oauth.providers.wechat_provider import WeChatProvider


class OAuthProviderFactory:
    """OAuth Provider 工厂

    使用工厂模式创建 Provider 实例，支持动态注册新的 Provider。
    """

    _providers: Dict[str, Type[BaseOAuthProvider]] = {
        "github": GitHubProvider,
        "google": GoogleProvider,
        "wechat": WeChatProvider,
        "dingtalk": DingTalkProvider,
        "feishu": FeishuProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseOAuthProvider]):
        """注册新的 provider（支持动态扩展）

        Args:
            name: Provider 名称
            provider_class: Provider 类
        """
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, provider: str) -> BaseOAuthProvider:
        """创建 provider 实例

        Args:
            provider: Provider 名称

        Returns:
            Provider 实例

        Raises:
            ValueError: 不支持的 provider
        """
        provider_class = cls._providers.get(provider)
        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider}")

        settings = get_settings()
        config = cls._get_config(provider, settings)
        return provider_class(config)

    @staticmethod
    def _get_config(provider: str, settings) -> OAuthConfig:
        """根据 provider 获取配置

        Args:
            provider: Provider 名称
            settings: 配置对象

        Returns:
            OAuthConfig 实例

        Raises:
            ValueError: 不支持的 provider
        """
        config_map = {
            "github": OAuthConfig(
                auth_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                user_url="https://api.github.com/user",
                client_id=settings.OAUTH_GITHUB_CLIENT_ID,
                client_secret=settings.OAUTH_GITHUB_CLIENT_SECRET,
                scope="user:email",
            ),
            "google": OAuthConfig(
                auth_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                user_url="https://www.googleapis.com/oauth2/v2/userinfo",
                client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
                client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
                scope="openid email profile",
            ),
            "wechat": OAuthConfig(
                auth_url="https://open.weixin.qq.com/connect/qrconnect",
                token_url="https://api.weixin.qq.com/sns/oauth2/access_token",
                user_url="https://api.weixin.qq.com/sns/userinfo",
                client_id=settings.OAUTH_WECHAT_APP_ID,
                client_secret=settings.OAUTH_WECHAT_APP_SECRET,
                scope="snsapi_login",
            ),
            "dingtalk": OAuthConfig(
                auth_url="https://login.dingtalk.com/oauth2/auth",
                token_url="https://api.dingtalk.com/v1.0/oauth2/userAccessToken",
                user_url="https://api.dingtalk.com/v1.0/contact/users/me",
                client_id=settings.OAUTH_DINGTALK_APP_ID,
                client_secret=settings.OAUTH_DINGTALK_APP_SECRET,
                scope="openid corpid",
            ),
            "feishu": OAuthConfig(
                auth_url="https://accounts.feishu.cn/open-apis/authen/v1/authorize",
                token_url="https://open.feishu.cn/open-apis/authen/v2/oauth/token",
                user_url="https://open.feishu.cn/open-apis/authen/v1/user_info",
                client_id=settings.OAUTH_FEISHU_APP_ID,
                client_secret=settings.OAUTH_FEISHU_APP_SECRET,
                scope="contact:user.base:readonly contact:user.email:readonly",
            ),
        }

        config = config_map.get(provider)
        if not config:
            raise ValueError(f"Unsupported provider: {provider}")

        return config

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """获取支持的 provider 列表

        Returns:
            Provider 名称列表
        """
        return list(cls._providers.keys())
