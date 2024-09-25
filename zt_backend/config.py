from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    run_mode: str = "app"
    project_name: str = ""
    user_name: str = ""
    ws_url: str = ""
    local_url: str = ""
    comments_enabled: bool = False
    show_create_button: bool = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()