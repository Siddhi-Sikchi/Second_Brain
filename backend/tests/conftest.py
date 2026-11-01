import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["SECRET_KEY"] = "test-secret-key-32-chars-long-12345"
os.environ["DATABASE_URL"] = "sqlite:///./test_second_brain.db"

from app.database import Base, get_db
from app.main import app

TEST_DB_PATH = Path("./test_second_brain.db")
test_engine = create_engine("sqlite:///./test_second_brain.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    user_payload = {
        "email": "student@university.edu",
        "password": "SecurePassword123!",
        "full_name": "Alex Student"
    }
    res = client.post("/api/auth/register", json=user_payload)
    data = res.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return {
        "user": data["user"],
        "token": token,
        "headers": headers,
        "raw_password": user_payload["password"]
    }
