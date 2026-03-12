from database import db
from datetime import datetime, timezone
import bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    decks = db.relationship('Deck', backref='owner', lazy=True, cascade='all, delete-orphan')
    otp_codes = db.relationship('OTPCode', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
        }

class OTPCode(db.Model):
    __tablename__ = 'otp_codes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)
    new_email = db.Column(db.String(255), nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc)

    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired()


class Deck(db.Model):
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))

    cards = db.relationship('Card', backref='deck', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('DeckProgress', backref='deck', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_cards=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'is_public': self.is_public,
            'card_count': len(self.cards),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        if include_cards:
            data['cards'] = [card.to_dict() for card in self.cards]
        return data

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, default=0)  # порядок картки в колоді
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'question': self.question,
            'answer': self.answer,
            'position': self.position,
            'created_at': self.created_at.isoformat(),
        }

class DeckProgress(db.Model):
    __tablename__ = 'deck_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    cards_studied = db.Column(db.Integer, default=0)  # скільки карток вивчено
    last_studied_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    card_statuses = db.relationship('CardProgress', backref='deck_progress', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (db.UniqueConstraint('user_id', 'deck_id'),)
    def to_dict(self):
        return {
            'deck_id': self.deck_id,
            'cards_studied': self.cards_studied,
            'last_studied_at': self.last_studied_at.isoformat() if self.last_studied_at else None,
        }

class CardProgress(db.Model):
    __tablename__ = 'card_progress'

    id = db.Column(db.Integer, primary_key=True)
    deck_progress_id = db.Column(db.Integer, db.ForeignKey('deck_progress.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    is_learned = db.Column(db.Boolean, default=False)
    times_seen = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('deck_progress_id', 'card_id'),)
    def to_dict(self):
        return {
            'card_id': self.card_id,
            'is_learned': self.is_learned,
            'times_seen': self.times_seen,
        }