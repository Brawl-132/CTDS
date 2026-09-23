from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database / MySQL
    mysqldump_path: str
    mysql_user: str
    mysql_password: str
    mysql_db: str
    mysql_table: str
    backup_interval: int = 3600  # default 1 hour

    # Other app settings
    database_url: str | None = None
    sqlite_url: str = "sqlite:///orders.db"
    debug: bool = False
    log_level: str = "INFO"
    excel_file_path: str = "Rollno.xlsx"
    photos_directory: str = "static/photos/"
    max_file_size: int = 10 * 1024 * 1024
    cache_ttl: int = 300

    class Config:
        env_file = ".env"
        extra = "allow"
        case_sensitive = False  # if your env vars are uppercase

settings = Settings()
