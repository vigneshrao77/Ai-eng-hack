import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///./data/test_modernrx.db"
os.environ["STANDALONE_LOCAL_MODE"] = "true"
os.environ["OFFLINE_DEMO_MODE"] = "true"
os.environ["USE_NEO4J"] = "false"

from app.main import app
from app.db.session import init_db, SessionLocal, Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    yield
    # Clean up test database
    Base.metadata.drop_all(bind=engine)
    test_db_file = Path("data/test_modernrx.db")
    if test_db_file.exists():
        try:
            test_db_file.unlink()
        except Exception:
            pass


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
