from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import check_db_health, get_db


async def test_get_db_generator() -> None:
    """Test get_db dependency yields an active session."""
    session_generator = get_db()
    session = await anext(session_generator)
    assert isinstance(session, AsyncSession)
    # Complete generator
    try:
        await anext(session_generator)
    except StopAsyncIteration:
        pass


async def test_check_db_health_failure() -> None:
    """Test check_db_health returns False when database connection fails."""
    with patch(
        "app.core.database.AsyncSessionLocal",
        side_effect=Exception("Database down"),
    ):
        result = await check_db_health()
        assert result is False


async def test_check_db_health_success() -> None:
    """Test check_db_health returns True when database responds."""
    mock_session = AsyncMock()
    mock_session.execute.return_value = None

    class MockSessionContext:
        async def __aenter__(self):
            return mock_session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch(
        "app.core.database.AsyncSessionLocal",
        return_value=MockSessionContext(),
    ):
        result = await check_db_health()
        assert result is True
