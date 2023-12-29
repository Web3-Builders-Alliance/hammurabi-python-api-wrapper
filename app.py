from flask import Flask
from routes.generate_key import generate_key
from routes.change_tier import change_tier
from routes.raw_transactions import raw_transaction_files
from routes.prices import price_files
from routes.metadata import metadata_files

app = Flask(__name__)

app.add_url_rule('/generate_api_key', view_func=generate_key, methods=['POST'])
app.add_url_rule('/change_tier', view_func=change_tier, methods=['POST'])
app.add_url_rule('/raw_transactions', view_func=raw_transaction_files, methods=['GET'])
app.add_url_rule('/prices', view_func=price_files, methods=['GET'])
app.add_url_rule('/metadata', view_func=metadata_files, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
