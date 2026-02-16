from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))
