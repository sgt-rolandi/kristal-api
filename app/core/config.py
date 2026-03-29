import os


class Settings:
    APP_NAME = os.getenv("APP_NAME", "KRISTAL API")
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))

    SECRET_KEY = os.getenv("SECRET_KEY", "KRISTAL_SUPER_SECRET_220416")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720")
    )

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kristal.db")


settings = Settings()