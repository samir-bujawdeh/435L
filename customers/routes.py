from flask import Blueprint, request, jsonify
from models import SessionLocal, Customer


app = Blueprint("customers", __name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route("/register", methods=["POST"])
def register_customer():
    db = next(get_db())
    data = request.json
    try:

        customer = Customer(
            full_name=data["full_name"],
            username=data["username"],
            password=data["password"],
            age=data["age"],
            address=data.get("address"),
            gender=data.get("gender"),
            marital_status=data.get("marital_status"),
            wallet=data.get("wallet", 0.0),
        )
        db.add(customer)
        db.commit()
        return jsonify({"message": "Customer registered successfully!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route("/", methods=["GET"])
def get_all_customers():
    db = next(get_db())
    customers = db.query(Customer).all()
    result = [
        {
            "id": customer.id,
            "full_name": customer.full_name,
            "username": customer.username,
            "age": customer.age,
            "address": customer.address,
            "gender": customer.gender,
            "marital_status": customer.marital_status,
            "wallet": customer.wallet,
        }
        for customer in customers
    ]
    return jsonify(result)


@app.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    db = next(get_db())
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(
        {
            "id": customer.id,
            "full_name": customer.full_name,
            "username": customer.username,
            "age": customer.age,
            "address": customer.address,
            "gender": customer.gender,
            "marital_status": customer.marital_status,
            "wallet": customer.wallet,
        }
    )

@app.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    db = next(get_db())
    data = request.json
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    try:
        customer.full_name = data.get("full_name", customer.full_name)
        customer.username = data.get("username", customer.username)
        customer.password = data.get("password", customer.password)
        customer.age = data.get("age", customer.age)
        customer.address = data.get("address", customer.address)
        customer.gender = data.get("gender", customer.gender)
        customer.marital_status = data.get("marital_status", customer.marital_status)
        customer.wallet = data.get("wallet", customer.wallet)
        db.commit()
        return jsonify({"message": "Customer updated successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    db = next(get_db())
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    try:
        db.delete(customer)
        db.commit()
        return jsonify({"message": "Customer deleted successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route("/<int:customer_id>/charge", methods=["POST"])
def charge_wallet(customer_id):
    db = next(get_db())
    data = request.json
    amount = data.get("amount")
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer.wallet += amount
        db.commit()
        return jsonify({"message": f"Wallet charged with {amount} successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/<int:customer_id>/deduct", methods=["POST"])
def deduct_wallet(customer_id):
    db = next(get_db())
    data = request.json
    amount = data.get("amount")
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    if customer.wallet < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    try:
        customer.wallet -= amount
        db.commit()
        return jsonify({"message": f"{amount} deducted from wallet successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()