import secrets
from datetime import datetime
from flask import request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app.api import api_bp
from app.extensions import db, csrf
from app.models import User, EmailCode, Deck, Card, StudyProgress
from app.utils import send_verification_code, validate_password_strength


def api_error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def api_ok(data=None, message=None):
    response = {"success": True}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), 200


@api_bp.route("/register", methods=["POST"])
@csrf.exempt
def api_register():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    username = body.get("username", "").strip()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    confirm = body.get("confirm_password", "")

    if not username or not email or not password or not confirm:
        return api_error("All fields are required.")

    if password != confirm:
        return api_error("Passwords do not match.")

    pw_errors = validate_password_strength(password)
    if pw_errors:
        return api_error(" ".join(pw_errors))

    if User.query.filter_by(email=email).first():
        return api_error("Email already registered.")

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    code = EmailCode.create_for_user(user, purpose="register")
    send_verification_code(user, code.code, purpose="register")

    return api_ok({"user_id": user.id}, "Account created. Check your email for a verification code.")


@api_bp.route("/verify-email", methods=["POST"])
@csrf.exempt
def api_verify_email():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    user_id = body.get("user_id")
    code_input = body.get("code", "")

    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    code_record = EmailCode.query.filter_by(
        user_id=user.id, purpose="register", is_used=False
    ).order_by(EmailCode.created_at.desc()).first()

    if not code_record or not code_record.is_valid() or code_record.code != code_input:
        return api_error("Invalid or expired code.")

    code_record.is_used = True
    user.is_verified = True
    db.session.commit()

    return api_ok(message="Email verified successfully.")


@api_bp.route("/login", methods=["POST"])
@csrf.exempt
def api_login():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return api_error("Invalid credentials.", 401)

    if not user.is_verified:
        return api_error("Please verify your email first.", 403)

    if user.two_fa_enabled:
        code = EmailCode.create_for_user(user, purpose="2fa")
        send_verification_code(user, code.code, purpose="2fa")
        return api_ok({"requires_2fa": True, "user_id": user.id}, "2FA code sent to email.")

    login_user(user)
    return api_ok(
        {"user_id": user.id, "username": user.username, "email": user.email},
        "Logged in successfully."
    )


@api_bp.route("/verify-2fa", methods=["POST"])
@csrf.exempt
def api_verify_2fa():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    user_id = body.get("user_id")
    code_input = body.get("code", "")

    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    code_record = EmailCode.query.filter_by(
        user_id=user.id, purpose="2fa", is_used=False
    ).order_by(EmailCode.created_at.desc()).first()

    if not code_record or not code_record.is_valid() or code_record.code != code_input:
        return api_error("Invalid or expired 2FA code.")

    code_record.is_used = True
    db.session.commit()
    login_user(user)

    return api_ok(
        {"user_id": user.id, "username": user.username, "email": user.email},
        "Logged in successfully."
    )


@api_bp.route("/decks", methods=["GET"])
@login_required
def api_get_decks():
    decks = Deck.query.filter_by(user_id=current_user.id).order_by(Deck.updated_at.desc()).all()
    progress_map = {
        p.deck_id: p
        for p in StudyProgress.query.filter_by(user_id=current_user.id).all()
    }

    result = []
    for deck in decks:
        p = progress_map.get(deck.id)
        result.append({
            "id": deck.id,
            "title": deck.title,
            "description": deck.description,
            "card_count": deck.card_count(),
            "cards_studied": p.cards_studied if p else 0,
            "completion_percent": p.completion_percent() if p else 0,
            "updated_at": deck.updated_at.isoformat(),
        })

    return api_ok(result)


@api_bp.route("/decks", methods=["POST"])
@login_required
@csrf.exempt
def api_create_deck():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    title = body.get("title", "").strip()
    if not title:
        return api_error("Title is required.")

    deck = Deck(
        user_id=current_user.id,
        title=title,
        description=body.get("description", ""),
    )
    db.session.add(deck)
    db.session.commit()

    return api_ok({"id": deck.id, "title": deck.title}, "Deck created.")


@api_bp.route("/decks/<int:deck_id>", methods=["PUT"])
@login_required
@csrf.exempt
def api_update_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    deck.title = body.get("title", deck.title).strip()
    deck.description = body.get("description", deck.description)
    db.session.commit()

    return api_ok({"id": deck.id, "title": deck.title}, "Deck updated.")


@api_bp.route("/decks/<int:deck_id>", methods=["DELETE"])
@login_required
@csrf.exempt
def api_delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    db.session.delete(deck)
    db.session.commit()
    return api_ok(message="Deck deleted.")


@api_bp.route("/decks/<int:deck_id>/cards", methods=["GET"])
@login_required
def api_get_cards(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    cards = [
        {"id": c.id, "question": c.question, "answer": c.answer}
        for c in deck.cards
    ]
    return api_ok(cards)


@api_bp.route("/decks/<int:deck_id>/cards", methods=["POST"])
@login_required
@csrf.exempt
def api_create_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    question = body.get("question", "").strip()
    answer = body.get("answer", "").strip()

    if not question or not answer:
        return api_error("Question and answer are required.")

    card = Card(deck_id=deck.id, question=question, answer=answer)
    db.session.add(card)
    db.session.commit()

    return api_ok({"id": card.id, "question": card.question, "answer": card.answer}, "Card added.")


@api_bp.route("/decks/<int:deck_id>/cards/<int:card_id>", methods=["PUT"])
@login_required
@csrf.exempt
def api_update_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    card = Card.query.get_or_404(card_id)
    if card.deck_id != deck.id:
        return api_error("Card not found in this deck.", 404)

    body = request.get_json()
    card.question = body.get("question", card.question).strip()
    card.answer = body.get("answer", card.answer).strip()
    db.session.commit()

    return api_ok({"id": card.id, "question": card.question, "answer": card.answer}, "Card updated.")


@api_bp.route("/decks/<int:deck_id>/cards/<int:card_id>", methods=["DELETE"])
@login_required
@csrf.exempt
def api_delete_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    card = Card.query.get_or_404(card_id)
    if card.deck_id != deck.id:
        return api_error("Card not found in this deck.", 404)

    db.session.delete(card)
    db.session.commit()
    return api_ok(message="Card deleted.")


@api_bp.route("/offline/<int:deck_id>", methods=["GET"])
@login_required
def api_offline_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    cards = [{"id": c.id, "question": c.question, "answer": c.answer} for c in deck.cards]
    progress = StudyProgress.query.filter_by(user_id=current_user.id, deck_id=deck_id).first()

    return api_ok({
        "deck": {
            "id": deck.id,
            "title": deck.title,
            "description": deck.description,
        },
        "cards": cards,
        "progress": {
            "cards_studied": progress.cards_studied if progress else 0,
            "cards_correct": progress.cards_correct if progress else 0,
            "completion_percent": progress.completion_percent() if progress else 0,
        }
    })


@api_bp.route("/sync-progress", methods=["POST"])
@login_required
@csrf.exempt
def api_sync_progress():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    deck_id = body.get("deck_id")
    cards_studied = body.get("cards_studied", 0)
    cards_correct = body.get("cards_correct", 0)

    deck = Deck.query.get(deck_id)
    if not deck or deck.user_id != current_user.id:
        return api_error("Deck not found.", 404)

    progress = StudyProgress.query.filter_by(user_id=current_user.id, deck_id=deck_id).first()
    if not progress:
        progress = StudyProgress(user_id=current_user.id, deck_id=deck_id)
        db.session.add(progress)

    progress.cards_studied = cards_studied
    progress.cards_correct = cards_correct
    progress.last_studied_at = datetime.utcnow()
    db.session.commit()

    return api_ok({
        "deck_id": deck_id,
        "cards_studied": progress.cards_studied,
        "completion_percent": progress.completion_percent(),
    }, "Progress synced.")
