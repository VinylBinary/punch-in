from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PUBLIC_KEY_BASE64: str
    BASE_URL: str
    LOGIN_USERNAME: str
    LOGIN_PASSWORD: str
    model_config = SettingsConfigDict(env_file=".env")


ENV_PROJECT = Settings()
