import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import SessionLocal, Customer, Base
from app import app
from sqlalchemy import create_engine
from flask import json

TEST_DATABASE_URL = "sqlite:///test_customers.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal.configure(bind=engine)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    db.add(Customer(
        full_name="John Doe",
        username="johndoe",
        password="securepassword123", 
        age=30,
        address="123 Main St",
        gender="Male",
        marital_status="Single",
        wallet=100.0
    ))
    db.commit()
    db.close()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["DATABASE_URL"] = TEST_DATABASE_URL
    with app.test_client() as client:
        yield client

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_register_customer(client, db):
    response = client.post("/customers/register", json={
        "full_name": "John Smith",
        "username": "johnsmith",
        "password": "securepassword123",
        "age": 30,
        "address": "456 Another St",
        "gender": "Male",
        "marital_status": "Married",
        "wallet": 200.0
    })
    print("Response status:", response.status_code)
    print("Response data:", response.get_json())
    assert response.status_code == 201



    data = json.loads(response.data)
    assert data["message"] == "Customer registered successfully!"

def test_get_all_customers(client, db):
    response = client.get("/customers/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

def test_update_customer(client, db):
    response = client.put("/customers/1", json={"age": 35})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Customer updated successfully!"

def test_delete_customer(client, db):
    response = client.delete("/customers/1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Customer deleted successfully!"
