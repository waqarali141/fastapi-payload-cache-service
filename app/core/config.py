from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
from typing import List, Union


# Read Environment variables from .env files into settings
class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_VERSION: str
    PROJECT_DESCRIPTION: str
    PROJECT_SUMMARY: str
    DB_URL: str

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
