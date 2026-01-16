"""
OAuth Provider 抽象基类

定义所有 OAuth Provider 必须实现的接口规范。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class OAuthConfig:
    """OAuth 配置数据类"""

    auth_url: str
    token_url: str
    user_url: str
    client_id: str
    client_secret: str
    scope: str


@dataclass
class OAuthUserInfo:
    """标准化用户信息"""

    provider_user_id: str
    email: Optional[str]
    phone: Optional[str]
    name: str
    avatar_url: Optional[str]


class BaseOAuthProvider(ABC):
    """OAuth Provider 抽象基类

    所有 OAuth Provider 必须继承此类并实现抽象方法。
    """

    def __init__(self, config: OAuthConfig):
        self.config = config

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider 名称"""
        pass

    @abstractmethod
    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """获取授权 URL

        Args:
            redirect_uri: 回调地址
            state: 防CSRF攻击的随机字符串

        Returns:
            授权 URL
        """
        pass

    @abstractmethod
    async def get_access_token(self, code: str, redirect_uri: str, client) -> str:
        """获取 access token

        Args:
            code: 授权码
            redirect_uri: 回调地址
            client: httpx.AsyncClient 实例

        Returns:
            access token

        Raises:
            ValueError: 获取失败时抛出异常
        """
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str, client) -> OAuthUserInfo:
        """获取用户信息

        Args:
            access_token: 访问令牌
            client: httpx.AsyncClient 实例

        Returns:
            标准化用户信息

        Raises:
            ValueError: 获取失败时抛出异常
        """
        pass

    def _extract_field(
        self, data: Dict, *keys: str, default: Optional[str] = None
    ) -> Optional[str]:
        """从字典中按优先级提取字段

        Args:
            data: 数据字典
            *keys: 字段名列表（按优先级）
            default: 默认值

        Returns:
            字段值或默认值
        """
        for key in keys:
            value = data.get(key)
            if value:
                return value
        return default
