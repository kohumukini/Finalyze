import pytest
from typing import NoReturn
from fastapi.testclient import TestClient

# Because pytest.ini starts at root directory
from backend.app import app
from backend.core.database import get_db_session

class FakeSession(): 
    def __getattr__(self, name) -> NoReturn:
        raise AssertionError(f"Test touched the database: Session.{name}")

@pytest.fixture
def client(): 
    app.dependency_overrides[get_db_session] = lambda: FakeSession()
    yield TestClient(app)
    app.dependency_overrides.clear()