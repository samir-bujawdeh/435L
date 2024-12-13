from flask import Flask
from routes import app as customers_blueprint


app = Flask(__name__)


app.register_blueprint(customers_blueprint, url_prefix="/customers")

if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=5001)



