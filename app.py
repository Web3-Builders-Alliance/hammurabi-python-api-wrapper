import logging
from flask import Flask
from routes.generate_key import generate_key_bp
from routes.change_tier import change_tier_bp
from routes.raw_transactions import raw_transactions_bp
from routes.prices import prices_bp
from routes.metadata import metadata_bp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

app.register_blueprint(change_tier_bp)
app.register_blueprint(prices_bp)
app.register_blueprint(metadata_bp)
app.register_blueprint(raw_transactions_bp)
app.register_blueprint(generate_key_bp)

if __name__ == '__main__':
    app.run(debug=True)
