from functools import lru_cache

class Settings:
    def __init__(self):
        self.run_mode = "app"
        self.project_name = ""
        self.user_name = ""
        self.team_name = ""
        self.ws_url = ""
        self.local_url = ""
        self.publish_url = "https://bxmm0wp9zk.execute-api.us-east-2.amazonaws.com/default/"
        self.comments_enabled = False
        self.show_create_button = False
        self.zt_path = ""

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
