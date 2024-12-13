from flask import Blueprint, request, jsonify
from models import SessionLocal, Review

app = Blueprint("reviews", __name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route("/add", methods=["POST"])
def add_review():
    db = next(get_db())
    data = request.json
    try:
        review = Review(
            item_id=data["item_id"],
            customer_id=data["customer_id"],
            rating=data["rating"],
            review=data.get("review"),
        )
        db.add(review)
        db.commit()
        return jsonify({"message": "Review added successfully!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route("/", methods=["GET"])
def get_all_reviews():
    db = next(get_db())
    reviews = db.query(Review).all()
    result = [
        {
            "id": review.id,
            "item_id": review.item_id,
            "customer_id": review.customer_id,
            "rating": review.rating,
            "review": review.review,
        }
        for review in reviews
    ]
    return jsonify(result)


@app.route("/item/<int:item_id>", methods=["GET"])
def get_reviews_by_item(item_id):
    db = next(get_db())
    reviews = db.query(Review).filter(Review.item_id == item_id).all()
    result = [
        {
            "id": review.id,
            "customer_id": review.customer_id,
            "rating": review.rating,
            "review": review.review,
        }
        for review in reviews
    ]
    return jsonify(result)


@app.route("/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    db = next(get_db())
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return jsonify({"error": "Review not found"}), 404
    try:
        db.delete(review)
        db.commit()
        return jsonify({"message": "Review deleted successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()
