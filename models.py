# sqlalchemy models for user and prompt tables
from app import db, app
from dataclasses import dataclass

# user table
# user_id, email, password, google_id, subscription_type, last_payment_date, next_payment_date, total_uses, remaining_uses, created_at
@dataclass
class User(db.Model):
    user_id: int
    email: str
    google_id: str
    subscription_type: str
    subscription_id: str
    customer_id: str
    last_payment_date: str
    last_payment_success: bool
    next_payment_date: str
    total_uses: int
    remaining_uses: int
    created_at: str

    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    subscription_type = db.Column(db.String(120), nullable=True, default='free')
    subscription_id = db.Column(db.String(120), nullable=True)
    customer_id = db.Column(db.String(120), nullable=True)
    last_payment_date = db.Column(db.DateTime, nullable=True)
    last_payment_success = db.Column(db.Boolean, nullable=True, default=False)
    next_payment_date = db.Column(db.DateTime, nullable=True)
    total_uses = db.Column(db.Integer, nullable=True)
    remaining_uses = db.Column(db.Integer, nullable=True, default=3)
    created_at = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp())



# prompt table
# prompt_id, prompt_test, response_text, user_id, created_at
@dataclass
class Prompt(db.Model):
    prompt_id: int
    prompt_text: str
    response_text: str
    user_id: int
    created_at: str

    __tablename__ = 'prompt'
    prompt_id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.String(120), nullable=True)
    response_text = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp())


# create the database tables
with app.app_context():
    db.create_all()

    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView
    admin = Admin(app, name='Data', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Prompt, db.session))
