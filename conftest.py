"""Tests use an isolated in-memory SQLite database, never real dormmate.db."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine
from app.database.db import get_session
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = test_session
    try:
        # Do not enter TestClient lifespan: app's real init_db is not needed here.
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
