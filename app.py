# flask app that uses flask-sqlalchemy to access a sqlite database
# and flask-admin to provide a web interface to the database

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL", 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "samba")
app.config['STRIPE_API_KEY'] = os.getenv("STRIPE_API_KEY", "sk_test_51MnJljBPTA2y06S6u0c7EBFilWsnEm8bHTDYtCsaIAQdinSAtzwtGj4Ka3NuKmKq1xuv11fQctXmbULTe2c6eYdU00xZ7rFxwP")
app.config['STRIPE_PRICE_PRO'] = os.getenv("STRIPE_PRICE_PRO", "price_1MnJnXBPTA2y06S6g75jx9Sj")
app.config['STRIPE_PRICE_BASIC'] = os.getenv("STRIPE_PRICE_BASIC", "price_1MnJnLBPTA2y06S6iPWiWE4y")
app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv("STRIPE_WEBHOOK_SECRET")
app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID")
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET")

db = SQLAlchemy(app)

import models, endpoints


# start the app
if __name__ == '__main__':
    flask_app.run()