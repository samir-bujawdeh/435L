from flask import Flask
from routes import app as sales_blueprint

app = Flask(__name__)


app.register_blueprint(sales_blueprint, url_prefix="/sales")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
