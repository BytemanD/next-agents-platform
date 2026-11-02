from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseModel):
    username: str = ""
    password: str = ""


class NapClientConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NAP_",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        frozen=True,
    )
    base_url: str = "http://localhost:18000"
    auth: AuthConfig = AuthConfig()


CONF = NapClientConfig()
