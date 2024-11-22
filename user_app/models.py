# user_app/models.py
from utils.db_utils import db
from werkzeug.security import generate_password_hash, check_password_hash


from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    portfolio = db.relationship('Portfolio', backref='user', lazy='dynamic')
    balance = db.Column(db.Float, nullable=False, default=100000.0)  # Added balance to User model

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False, default=100000.0)
    change = db.Column(db.Float, nullable=False, default=0.0)