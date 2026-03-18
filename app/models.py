from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    two_fa_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    decks = db.relationship("Deck", backref="owner", lazy=True, cascade="all, delete-orphan")
    progress = db.relationship("StudyProgress", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class EmailCode(db.Model):
    __tablename__ = "email_codes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)
    new_email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="email_codes")

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    @staticmethod
    def create_for_user(user, purpose, expiry_minutes=15, new_email=None):
        import secrets
        EmailCode.query.filter_by(user_id=user.id, purpose=purpose, is_used=False).delete()
        code = EmailCode(
            user_id=user.id,
            code=str(secrets.randbelow(900000) + 100000),
            purpose=purpose,
            new_email=new_email,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes),
        )
        db.session.add(code)
        db.session.commit()
        return code

    def __repr__(self):
        return f"<EmailCode {self.purpose} for user {self.user_id}>"


class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cards = db.relationship("Card", backref="deck", lazy=True, cascade="all, delete-orphan")
    progress = db.relationship("StudyProgress", backref="deck", lazy=True, cascade="all, delete-orphan")

    def card_count(self):
        return len(self.cards)

    def __repr__(self):
        return f"<Deck {self.title}>"



