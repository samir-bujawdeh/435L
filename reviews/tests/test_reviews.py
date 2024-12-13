import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import SessionLocal, Review, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)

    with app.test_client() as client:
        yield client

    Base.metadata.drop_all(bind=engine)


def test_add_review(client):
    response = client.post("/reviews/add", json={
        "customer_id": 1,
        "item_id": 1,
        "rating": 4,
        "review": "Good product"
    })
    assert response.status_code == 201
    assert response.json["message"] == "Review added successfully!"


def test_get_all_reviews(client):
    client.post("/reviews/add", json={"customer_id": 1, "item_id": 1, "rating": 4, "review": "Good"})
    client.post("/reviews/add", json={"customer_id": 2, "item_id": 1, "rating": 5, "review": "Excellent!"})

    response = client.get("/reviews/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    assert data[0]["review"] == "Good"


def test_get_reviews_by_item(client):
    client.post("/reviews/add", json={"customer_id": 1, "item_id": 1, "rating": 4, "review": "Good"})
    client.post("/reviews/add", json={"customer_id": 2, "item_id": 1, "rating": 5, "review": "Excellent!"})

    response = client.get("/reviews/item/1")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    assert data[1]["review"] == "Excellent!"


def test_delete_review(client):
    client.post("/reviews/add", json={"customer_id": 1, "item_id": 1, "rating": 4, "review": "Good"})
    client.post("/reviews/add", json={"customer_id": 2, "item_id": 1, "rating": 5, "review": "Excellent!"})

    response = client.delete("/reviews/1")
    assert response.status_code == 200
    assert response.json["message"] == "Review deleted successfully!"

    response = client.get("/reviews/")
    data = response.json
    assert len(data) == 1