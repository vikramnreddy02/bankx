from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql://user:password@postgres:5432/userdb",
        env="DATABASE_URL"
    )

    class Config:
        case_sensitive = True

settings = Settings()
