import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import SessionLocal, Sale, Base
from app import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import json
from unittest.mock import patch

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


@patch("routes.requests.post")
def test_add_sale(mock_post, client):
   
    mock_post.side_effect = [

        type("Response", (object,), {"status_code": 200, "json": lambda: {}})(),
        
        type("Response", (object,), {"status_code": 200, "json": lambda: {}})(),
    ]

    
    response = client.post("/sales/add", json={
        "customer_id": 1,
        "item_id": 1,
        "quantity": 2,
        "total_price": 50.0
    })
    assert response.status_code == 201
    assert response.json["message"] == "Sale recorded successfully!"


@patch("routes.requests.post")
def test_add_sale_missing_fields(mock_post, client):
    response = client.post("/sales/add", json={
        "customer_id": 1,
        "quantity": 2
    })
    assert response.status_code == 400
    assert response.json["error"] == "Missing required fields"



def test_get_all_sales(client):
   
    db = SessionLocal()
    db.add(Sale(customer_id=1, item_id=1, quantity=2, total_price=50.0))
    db.add(Sale(customer_id=2, item_id=2, quantity=1, total_price=30.0))
    db.commit()
    db.close()


    response = client.get("/sales/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    assert data[0]["customer_id"] == 1
    assert data[1]["customer_id"] == 2


def test_get_sale(client):

    db = SessionLocal()
    sale = Sale(customer_id=1, item_id=1, quantity=2, total_price=50.0)
    db.add(sale)
    db.commit()
    sale_id = sale.id
    db.close()


    response = client.get(f"/sales/{sale_id}")
    assert response.status_code == 200
    assert response.json["customer_id"] == 1
    assert response.json["item_id"] == 1
    assert response.json["quantity"] == 2
    assert response.json["total_price"] == 50.0

    response = client.get("/sales/999")
    assert response.status_code == 404
    assert response.json["error"] == "Sale not found"