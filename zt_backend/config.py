from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    run_mode: str = "app"
    project_name: str = ""
    user_name: str = ""
    ws_url: str = ""

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()