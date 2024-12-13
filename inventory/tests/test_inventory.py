import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base
from app import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import json


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    global SessionLocal
    SessionLocal = TestingSessionLocal

    with app.test_client() as client:
        yield client


def test_add_item(client):
    response = client.post("/inventory/add", json={"name": "Test Item", "quantity": 10, "price": 15.5})
    assert response.status_code == 201
    assert response.json.get("message") == "Item added successfully!"



def test_update_item(client):
    response = client.post("/inventory/add", json={"name": "Item 1", "quantity": 10, "price": 10.0})
    item_id = response.json.get("id")
    assert item_id is not None

    response = client.put(f"/inventory/{item_id}", json={"quantity": 15, "price": 12.0})
    assert response.status_code == 200
    assert response.json.get("message") == "Item updated successfully!"


def test_delete_item(client):
    response = client.post("/inventory/add", json={"name": "Item 1", "quantity": 10, "price": 10.0})
    item_id = response.json.get("id")
    assert item_id is not None

    response = client.delete(f"/inventory/{item_id}")
    assert response.status_code == 200
    assert response.json.get("message") == "Item deleted successfully!"