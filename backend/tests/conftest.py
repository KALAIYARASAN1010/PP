import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.models import User, Proposal, DecisionHistory, AuditLog
from backend.app.seed_data import seed_database
from backend.app.auth import create_access_token

# In-memory SQLite database for isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
import backend.app.database as db_module
db_module.engine = engine
db_module.SessionLocal = TestingSessionLocal

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
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
def submitter_token(db_session):
    user = db_session.query(User).filter(User.username == "officer_chen").first()
    return create_access_token({"sub": user.username, "user_id": user.id, "role": user.role})

@pytest.fixture
def submitter_headers(submitter_token):
    return {"Authorization": f"Bearer {submitter_token}"}

@pytest.fixture
def reviewer_token(db_session):
    user = db_session.query(User).filter(User.username == "captain_miller").first()
    return create_access_token({"sub": user.username, "user_id": user.id, "role": user.role})

@pytest.fixture
def reviewer_headers(reviewer_token):
    return {"Authorization": f"Bearer {reviewer_token}"}

@pytest.fixture
def admin_token(db_session):
    user = db_session.query(User).filter(User.username == "admin_patel").first()
    return create_access_token({"sub": user.username, "user_id": user.id, "role": user.role})

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
