from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Inventory Backend"
    sqlite_path: str = "./data/app.db"
    # Email settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = ""
    owner_email: str = ""

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # Favicon (external URL)
    favicon_url: str = ""

    # Tax config
    total_tax_rate_percent: float = 30.0

    # CORS
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
