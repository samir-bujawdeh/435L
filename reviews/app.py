from flask import Flask
from routes import app as reviews_blueprint

app = Flask(__name__)


app.register_blueprint(reviews_blueprint, url_prefix="/reviews")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
