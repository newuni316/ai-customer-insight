"""应用配置 - 安全加固版"""
import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache
import warnings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./insight.db"
    SECRET_KEY: str = ""  # 空则自动生成
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    AI_API_KEY: str = ""
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"
    AUTO_MIGRATE: bool = False

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SECRET_KEY:
            self.SECRET_KEY = secrets.token_hex(32)
            warnings.warn("SECRET_KEY 未设置，已自动生成随机密钥（重启后失效）。生产环境请设置固定密钥。")


@lru_cache
def get_settings() -> Settings:
    return Settings()
