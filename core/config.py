from pydantic import BaseSettings


class Settings(BaseSettings):
    db_user: str = "habrpguser"
    db_password: str = "pgpwd4habr"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "todo"


settings = Settings()

ASYNC_DATABASE_URI = (
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)
SYNC_DATABASE_URI = (
    f"postgresql://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)
