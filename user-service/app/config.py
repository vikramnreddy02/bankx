from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # read from env; provide sane local defaults
    database_url: str = Field(
        default="postgresql://user:password@postgres:5432/userdb",
        env="DATABASE_URL"
    )

    class Config:
        case_sensitive = True

settings = Settings()

