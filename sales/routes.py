import requests
from flask import Blueprint, request, jsonify
from models import SessionLocal, Sale

app = Blueprint("sales", __name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

CUSTOMERS_SERVICE_URL = "http://127.0.0.1:5001/customers"

INVENTORY_SERVICE_URL = "http://127.0.0.1:5002/inventory"


@app.route("/add", methods=["POST"])
def add_sale():
    db = next(get_db())
    data = request.json


    customer_id = data.get("customer_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity")
    total_price = data.get("total_price")

    if not (customer_id and item_id and quantity and total_price):
        return jsonify({"error": "Missing required fields"}), 400

    
    try:
        wallet_response = requests.post(
            f"{CUSTOMERS_SERVICE_URL}/{customer_id}/deduct",
            json={"amount": total_price}
        )
        if wallet_response.status_code != 200:
            return jsonify({"error": wallet_response.json().get("error", "Wallet deduction failed")}), wallet_response.status_code
    except Exception as e:
        return jsonify({"error": f"Failed to connect to Customers Service: {str(e)}"}), 500

    try:
        stock_response = requests.post(
            f"{INVENTORY_SERVICE_URL}/{item_id}/deduct",
            json={"quantity": quantity}
        )
        if stock_response.status_code != 200:
            return jsonify({"error": stock_response.json().get("error", "Stock deduction failed")}), stock_response.status_code
    except Exception as e:
        return jsonify({"error": f"Failed to connect to Inventory Service: {str(e)}"}), 500

 
    try:
        sale = Sale(
            customer_id=customer_id,
            item_id=item_id,
            quantity=quantity,
            total_price=total_price
        )
        db.add(sale)
        db.commit()
        return jsonify({"message": "Sale recorded successfully!", "sale_id": sale.id}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@app.route("/", methods=["GET"])
def get_all_sales():
    db = next(get_db())
    sales = db.query(Sale).all()
    result = [
        {
            "id": sale.id,
            "item_id": sale.item_id,
            "customer_id": sale.customer_id,
            "quantity": sale.quantity,
            "total_price": sale.total_price,
            "sale_date": sale.sale_date,
        }
        for sale in sales
    ]
    return jsonify(result)


@app.route("/<int:sale_id>", methods=["GET"])
def get_sale(sale_id):
    db = next(get_db())
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        return jsonify({"error": "Sale not found"}), 404
    return jsonify(
        {
            "id": sale.id,
            "item_id": sale.item_id,
            "customer_id": sale.customer_id,
            "quantity": sale.quantity,
            "total_price": sale.total_price,
            "sale_date": sale.sale_date,
        }
    )
