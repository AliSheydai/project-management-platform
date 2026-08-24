from app.core.config import Settings, parse_cors


def test_parse_cors_strings() -> None:
    assert parse_cors("http://localhost:3000,http://127.0.0.1:3000") == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    assert parse_cors('["http://localhost:3000"]') == ["http://localhost:3000"]
    assert parse_cors(["http://localhost:3000"]) == ["http://localhost:3000"]


def test_settings_defaults() -> None:
    settings = Settings(
        PROJECT_NAME="Test App",
        DATABASE_URL="postgresql+asyncpg://postgres:postgrespassword@localhost:5432/test_db",
        REDIS_URL="redis://localhost:6379/1",
    )
    assert settings.PROJECT_NAME == "Test App"
    assert settings.SQLALCHEMY_DATABASE_URI.startswith("postgresql+asyncpg://")
    assert settings.REDIS_CONNECTION_URL == "redis://localhost:6379/1"
