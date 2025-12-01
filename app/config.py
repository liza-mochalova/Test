from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./lab_inventory.db"
    
    class Config:
        env_file = ".env"

settings = Settings()