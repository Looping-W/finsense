import os
from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class Config:
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    jwt_secret: str
    jwt_expires_days: int
    cors_origins: list[str]
    flask_port: int


def load_config() -> Config:
    origins = [
        item.strip()
        for item in os.getenv(
            "CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
        ).split(",")
        if item.strip()
    ]
    return Config(
        mysql_host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        mysql_port=int(os.getenv("MYSQL_PORT", "3306")),
        mysql_user=os.getenv("MYSQL_USER", "root"),
        mysql_password=os.getenv("MYSQL_PASSWORD", ""),
        mysql_database=os.getenv("MYSQL_DATABASE", "finsense"),
        jwt_secret=os.getenv("JWT_SECRET", ""),
        jwt_expires_days=int(os.getenv("JWT_EXPIRES_DAYS", "7")),
        cors_origins=origins,
        flask_port=int(os.getenv("FLASK_PORT", "5000")),
    )


def sqlalchemy_database_uri(config: Config) -> str:
    user = quote_plus(config.mysql_user)
    password = quote_plus(config.mysql_password)
    return (
        f"mysql+pymysql://{user}:{password}@{config.mysql_host}:{config.mysql_port}/"
        f"{config.mysql_database}?charset=utf8mb4"
    )
