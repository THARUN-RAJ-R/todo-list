from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from .main import app,get_db
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

from sqlalchemy.orm import declarative_base

Base = declarative_base()

Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    
def test_update_blog(client: TestClient, db_session: Session):
    blog = models.Blog(title="Old Title", body="Old Body")
    db_session.add(blog)
    db_session.commit()
    db_session.refresh(blog)
    
    response = client.put(f"/blog/{blog.id}", data={"title": "Updated Title", "body": "Updated Body"})
    assert response.status_code == 202  
    updated_blog = db_session.query(models.Blog).filter_by(id=blog.id).first()
    assert updated_blog.title == "Updated Title"
    assert updated_blog.body == "Updated Body"

def test_delete_blog(client: TestClient, db_session: Session):
    blog = models.Blog(title="Title to Delete", body="Body to Delete")
    db_session.add(blog)
    db_session.commit()
    db_session.refresh(blog)
    
    response = client.delete(f"/blog/{blog.id}")
    assert response.status_code == 204
    
    deleted_blog = db_session.query(models.Blog).filter_by(id=blog.id).first()
    assert deleted_blog is None
