from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Login Demo API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/login_demo"
    )

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天

    # SMTP配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_CODE_EXPIRE_MINUTES: int = 5

    # 短信配置 (短信宝)
    SMSBAO_USERNAME: str = ""
    SMSBAO_PASSWORD: str = ""
    SMSBAO_URL: str = "http://api.smsbao.com/"
    SMSBAO_TEMPLATE: str = "【Login Demo】您的验证码是：{}，请勿泄露给他人。"
    SMSBAO_CODE_EXPIRE_MINUTES: int = 1

    # OAuth配置
    OAUTH_GITHUB_CLIENT_ID: str = ""
    OAUTH_GITHUB_CLIENT_SECRET: str = ""
    OAUTH_GOOGLE_CLIENT_ID: str = ""
    OAUTH_GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_WECHAT_APP_ID: str = ""
    OAUTH_WECHAT_APP_SECRET: str = ""
    OAUTH_DINGTALK_APP_ID: str = ""
    OAUTH_DINGTALK_APP_SECRET: str = ""
    OAUTH_FEISHU_APP_ID: str = ""
    OAUTH_FEISHU_APP_SECRET: str = ""
    OAUTH_ALIPAY_APP_ID: str = ""
    OAUTH_ALIPAY_PRIVATE_KEY: str = ""
    OAUTH_ALIPAY_PUBLIC_KEY: str = ""

    # CORS配置
    CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
