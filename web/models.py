from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable = False)
    email = db.Column(db.String(150), unique=True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_strongpassword(self, password):
        if len(password) < 8:
            return False, "Too short"

        if not any(c.isupper() for c in password):
            return False, "No uppercase letter"

        if not any(c.isdigit() for c in password):
            return False, "No number"

        if not any(not c.isalnum() for c in password):
            return False, "No special character"

        return True




