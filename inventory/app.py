from flask import Flask
from routes import app as inventory_blueprint

app = Flask(__name__)

app.register_blueprint(inventory_blueprint, url_prefix="/inventory")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
