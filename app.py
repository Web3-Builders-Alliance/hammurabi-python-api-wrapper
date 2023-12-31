from flask import Flask
from routes.generate_key import generate_key
from routes.change_tier import change_tier_bp
from routes.raw_transactions import raw_transactions_bp
from routes.prices import prices_bp
from routes.metadata import metadata_bp

app = Flask(__name__)

app.register_blueprint(change_tier_bp)
app.register_blueprint(prices_bp)
app.register_blueprint(metadata_bp)
app.register_blueprint(raw_transactions_bp)

app.add_url_rule('/generate_api_key', view_func=generate_key, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
