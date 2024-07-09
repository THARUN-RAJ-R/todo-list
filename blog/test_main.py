from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from .main import app,get_db
from .database import Base
from fastapi import Form
from . import models
import pytest


client = TestClient(app)

DATABASE_URL ="sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Test_Blog(Base):
    __tablename__ = "test_blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)

@pytest.fixture(scope="module")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="module")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def setup() -> None:
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    Base.metadata.drop_all(bind=engine)

def test_get_all_blogs(client: TestClient, db_session: Session):

    blog1 = models.Blog(title="Test Blog 1", body="Test Body 1")
    blog2 = models.Blog(title="Test Blog 2", body="Test Body 2")
    db_session.add(blog1)
    db_session.add(blog2)
    db_session.commit()
    
    response = client.get("/blog")
    assert response.status_code == 200
    assert "Test Blog 1" in response.text
    assert "Test Blog 2" in response.text


def test_create_blog(client: TestClient, db_session: Session):
    response = client.post("/blog", data={"title": "New Blog", "body": "New Body"})
    assert response.status_code == 201
    new_blog = db_session.query(models.Blog).filter_by(title="New Blog").first()
    assert new_blog is not None
    assert new_blog.title == "New Blog"
    assert new_blog.body == "New Body"
    



