from flask import Flask
from flask_cors import CORS

from routes.auth import auth_bp
from routes.wallet import wallet_bp
from routes.transaction import transaction_bp
from routes.budget import budget_bp
from routes.crypto import crypto_bp
from routes.analytics import analytics_bp
from routes.transfer import transfer_bp

from datetime import datetime, date

app = Flask(__name__)
CORS(app)

class ISTJSONProvider(app.json_provider_class):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S+05:30')
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)

app.json = ISTJSONProvider(app)

app.register_blueprint(auth_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(crypto_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(transfer_bp)


@app.route("/")
def home():
    return {"message": "SmartWallet API running"}


if __name__ == "__main__":
    app.run(debug=True)