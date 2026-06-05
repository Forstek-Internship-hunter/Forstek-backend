from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_URL: str
    REDIS_URL: str
    GROQ_API_KEY: str
    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()