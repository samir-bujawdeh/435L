from flask import Blueprint, request, jsonify
from models import SessionLocal, Item

app = Blueprint("inventory", __name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route("/add", methods=["POST"])
def add_item():
    db = next(get_db())
    data = request.json
    try:
        item = Item(
            name=data["name"],
            quantity=data["quantity"],
            price=data["price"],
            description=data.get("description"),
        )
        db.add(item)
        db.commit()
        return jsonify({
            "message": "Item added successfully!",
            "id": item.id 
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()



@app.route("/", methods=["GET"])
def get_items():
    db = next(get_db())
    items = db.query(Item).all()
    result = [
        {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "price": item.price,
            "description": item.description,
        }
        for item in items
    ]
    return jsonify(result)

@app.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    db = next(get_db())
    data = request.json
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    try:
        item.name = data.get("name", item.name)
        item.quantity = data.get("quantity", item.quantity)
        item.price = data.get("price", item.price)
        item.description = data.get("description", item.description)
        db.commit()
        return jsonify({"message": "Item updated successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    db = next(get_db())
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    try:
        db.delete(item)
        db.commit()
        return jsonify({"message": "Item deleted successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route("/<int:item_id>/deduct", methods=["POST"])
def deduct_stock(item_id):
    db = next(get_db())
    data = request.json
    quantity_to_deduct = data.get("quantity")
    if not quantity_to_deduct or quantity_to_deduct <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404

    if item.quantity < quantity_to_deduct:
        return jsonify({"error": "Insufficient stock"}), 400

    try:
        item.quantity -= quantity_to_deduct
        db.commit()
        return jsonify({"message": f"{quantity_to_deduct} items deducted from stock successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
