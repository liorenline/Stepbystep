from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager
import secrets


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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    email = db.Column(db.String(120), nullable=False)

    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    is_used = db.Column(db.Boolean, default=False)

    @staticmethod
    def create(email, purpose):
        code = str(secrets.randbelow(1000000)).zfill(6)

        record = EmailCode(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )

        db.session.add(record)
        db.session.commit()
        return record

    def is_valid(self):
        return (not self.is_used) and datetime.utcnow() < self.expires_at


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

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Card {self.id} in deck {self.deck_id}>"


class StudyProgress(db.Model):
    __tablename__ = "study_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    cards_studied = db.Column(db.Integer, default=0)
    cards_correct = db.Column(db.Integer, default=0)
    last_studied_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "deck_id", name="unique_user_deck"),)

    def completion_percent(self):
        total = self.deck.card_count()
        if total == 0:
            return 0
        return round((self.cards_studied / total) * 100)

    def __repr__(self):
        return f"<StudyProgress user={self.user_id} deck={self.deck_id}>"

